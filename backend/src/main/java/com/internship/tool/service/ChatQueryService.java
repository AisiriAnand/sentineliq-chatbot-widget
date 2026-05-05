package com.internship.tool.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.internship.tool.entity.ChatQuery;
import com.internship.tool.repository.ChatQueryRepository;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;
import java.util.concurrent.CompletableFuture;

@Service
public class ChatQueryService {

    private final ChatQueryRepository chatQueryRepository;
    private final AiServiceClient aiServiceClient;
    private final ObjectMapper objectMapper;

    public ChatQueryService(ChatQueryRepository chatQueryRepository, AiServiceClient aiServiceClient) {
        this.chatQueryRepository = chatQueryRepository;
        this.aiServiceClient = aiServiceClient;
        this.objectMapper = new ObjectMapper();
    }

    @Transactional
    public ChatQuery createChatQuery(String userInput) {
        ChatQuery chatQuery = new ChatQuery(userInput);
        chatQuery.setStatus("processing");
        ChatQuery saved = chatQueryRepository.save(chatQuery);

        callAiServicesAsync(saved.getId(), userInput);

        return saved;
    }

    @Async
    public void callAiServicesAsync(Long chatQueryId, String userInput) {
        try {
            CompletableFuture<Map<String, Object>> describeFuture = aiServiceClient.describeAsync(userInput);
            CompletableFuture<Map<String, Object>> recommendFuture = aiServiceClient.recommendAsync(userInput);

            CompletableFuture.allOf(describeFuture, recommendFuture).join();

            Map<String, Object> describeResult = describeFuture.get();
            Map<String, Object> recommendResult = recommendFuture.get();

            ChatQuery chatQuery = chatQueryRepository.findById(chatQueryId).orElse(null);
            if (chatQuery != null) {
                if (describeResult != null) {
                    try {
                        String descriptionJson = objectMapper.writeValueAsString(describeResult);
                        chatQuery.setAiDescription(descriptionJson);
                    } catch (Exception e) {
                        System.err.println("Failed to serialize describe result: " + e.getMessage());
                    }
                }

                if (recommendResult != null) {
                    try {
                        String recommendationsJson = objectMapper.writeValueAsString(recommendResult);
                        chatQuery.setAiRecommendations(recommendationsJson);
                    } catch (Exception e) {
                        System.err.println("Failed to serialize recommend result: " + e.getMessage());
                    }
                }

                chatQuery.setStatus("completed");
                chatQueryRepository.save(chatQuery);
            }
        } catch (Exception e) {
            System.err.println("AI service integration failed: " + e.getMessage());

            ChatQuery chatQuery = chatQueryRepository.findById(chatQueryId).orElse(null);
            if (chatQuery != null) {
                chatQuery.setStatus("failed");
                chatQueryRepository.save(chatQuery);
            }
        }
    }
}

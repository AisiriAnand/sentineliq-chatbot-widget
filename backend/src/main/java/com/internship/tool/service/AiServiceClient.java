package com.internship.tool.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

@Service
public class AiServiceClient {

    @Value("${ai.service.url:http://localhost:5000}")
    private String aiServiceUrl;

    private final RestTemplate restTemplate;

    public AiServiceClient() {
        this.restTemplate = new RestTemplate();
    }

    @Async
    public CompletableFuture<Map<String, Object>> describeAsync(String userInput) {
        try {
            String url = UriComponentsBuilder.fromHttpUrl(aiServiceUrl)
                    .path("/describe")
                    .toUriString();

            Map<String, String> request = new HashMap<>();
            request.put("user_input", userInput);

            ResponseEntity<Map> response = restTemplate.postForEntity(url, request, Map.class);

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return CompletableFuture.completedFuture(response.getBody());
            }
        } catch (Exception e) {
            System.err.println("AI Service /describe failed: " + e.getMessage());
        }
        return CompletableFuture.completedFuture(null);
    }

    @Async
    public CompletableFuture<Map<String, Object>> recommendAsync(String userInput) {
        try {
            String url = UriComponentsBuilder.fromHttpUrl(aiServiceUrl)
                    .path("/recommend")
                    .toUriString();

            Map<String, String> request = new HashMap<>();
            request.put("user_input", userInput);

            ResponseEntity<Map> response = restTemplate.postForEntity(url, request, Map.class);

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return CompletableFuture.completedFuture(response.getBody());
            }
        } catch (Exception e) {
            System.err.println("AI Service /recommend failed: " + e.getMessage());
        }
        return CompletableFuture.completedFuture(null);
    }
}

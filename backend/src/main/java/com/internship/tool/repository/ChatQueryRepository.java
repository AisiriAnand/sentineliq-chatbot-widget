package com.internship.tool.repository;

import com.internship.tool.entity.ChatQuery;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ChatQueryRepository extends JpaRepository<ChatQuery, Long> {
}

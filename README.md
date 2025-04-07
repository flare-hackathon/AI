# Flare AI Hackathon Project - AI Scoring Module

## Overview

This repository contains the AI scoring component for a decentralized content sharing platform built on Flare. The AI agent reviews and scores blog posts on a daily basis, influencing content visibility and token rewards distribution. As the AI agent holds 50% of the total token supply, its scoring decisions have significant impact on the platform ecosystem.

### Features

- **Automated Content Review**: Daily analysis of all platform blog posts
- **Quality Assessment**: Scoring based on content quality, engagement metrics, and predefined parameters
- **Reward Influence**: High-scoring content receives greater visibility and token rewards
- **Scheduled Execution**: Automated daily scoring through cronjob implementation

## Technical Overview

### Architecture

The AI scoring module consists of:

1. **Data Fetcher**: Retrieves posts from the blockchain/database
2. **Content Analyzer**: Natural language processing pipeline to evaluate post quality
3. **Engagement Analyzer**: Measures user interaction metrics
4. **Score Calculator**: Combines various factors to generate final scores
5. **Blockchain Interface**: Publishes scores back to the smart contract

## Scoring Algorithm

The AI agent utilizes a comprehensive scoring system that evaluates content across multiple dimensions:

```
Final Score = (0.35 * Content Quality) + (0.25 * User Engagement) + 
              (0.20 * Originality) + (0.15 * Relevance) + (0.05 * Timeliness)
```

Each component is evaluated using advanced LLM analysis:

- **Content Quality**: Assesses clarity, coherence, depth, and writing quality
- **User Engagement**: Analyzes user votes, comments, view metrics, and time spent
- **Originality**: Evaluates uniqueness and innovation in content
- **Relevance**: Measures alignment with specified tags and platform focus
- **Timeliness**: Factors in content recency and topic currency

## Smart Contract Interaction

The AI agent interacts with the blockchain in the following ways:

1. **Authentication**: Uses a secured wallet to sign transactions
2. **Function Calls**: Invokes the function to score the User's post
3. **Transaction Verification**: Confirms successful execution of scoring transactions

## Configuration

The system requires several configuration parameters:

1. **LLM Settings**:

   - API key
   - Model selection
   - Temperature settings
2. **Blockchain Connection**:

   - RPC endpoint URL
   - Contract address
   - Wallet private key (securely stored)
3. **Scoring Parameters**:

   - Component weights
   - Thresholds for various metrics
   - Batch processing limits

## Monitoring & Logging

The system should include comprehensive monitoring:

- **Performance Tracking**: Measures scoring accuracy and consistency
- **Resource Usage**: Monitors API call volumes and costs
- **Error Handling**: Logs and alerts for failed transactions

## Development Roadmap

### Core Implementation

- [ ] LLM integration setup
- [ ] Duplication checks among posts
- [ ] Relevance Check for post
- [ ] Basic scoring algorithm
- [ ] Smart contract interaction
- [ ] Scheduled execution via Cronjob
- [ ] Wallet Integration with the AI agent
- [ ] Transaction Triggers, Checks
- [ ] Error Handling and Logging

### Potential Features: 
- [ ] Web Search to check and compare for originality
- [ ] Enhanced Scoring Algorithm with WebSearch based originality scores.
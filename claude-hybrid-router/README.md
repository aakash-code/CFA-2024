# Claude Hybrid Router 🚀

**Intelligent LLM routing for maximum cost savings and performance**

Route your Claude Code requests between free local models (Ollama), free cloud models (OpenRouter), and premium Claude API based on task complexity. Save 80-95% on API costs while maintaining quality.

## 💡 Overview

```
Your Request → Router → Best Model for the Job
                 ├─→ Ollama (Local/Free) ......... 80% of tasks
                 ├─→ OpenRouter (Free Cloud) ..... 15% of tasks
                 └─→ Claude API (Premium) ........ 5% of tasks
```

### Cost Comparison

| Approach | Daily Cost | Monthly Cost | Notes |
|----------|------------|--------------|-------|
| **Claude API only** | $15-25 | $450-750 | Premium quality, high cost |
| **Hybrid Router** | $0.50-2 | $15-60 | 95% savings, smart routing |
| **Local only** | $0 | $0 | Free, limited capabilities |

## 🎯 Features

- **Intelligent Routing**: Automatically routes requests based on complexity, context size, and tools needed
- **Cost Optimization**: 80-95% cost savings compared to using Claude API for everything
- **Fallback Support**: Gracefully falls back to cloud models when local is unavailable
- **Real-time Monitoring**: Track costs, performance, and routing decisions
- **Zero Configuration**: Works out-of-the-box with sensible defaults
- **Flexible**: Easy to customize routing rules for your workflow

## 📋 Prerequisites

- **OS**: Linux/macOS (Windows with WSL)
- **RAM**: 8GB minimum (16GB+ recommended for larger models)
- **Disk**: 50GB free space (for models)
- **Python**: 3.8+
- **Optional**: API keys for OpenRouter and/or Anthropic

## 🚀 Quick Start

### 1. Run Setup Script

```bash
cd /root/claude-hybrid-router
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This will:
- ✅ Install Ollama if needed
- ✅ Download recommended models (Qwen 2.5 Coder, DeepSeek Coder)
- ✅ Create configuration files
- ✅ Test the router

### 2. Configure API Keys (Optional)

Edit `.env` file:

```bash
nano /root/claude-hybrid-router/config/.env
```

Add your API keys:
```bash
# For free cloud backup
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# For premium tasks (optional)
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

> **Tip**: You can run 100% free with just Ollama! OpenRouter and Anthropic are optional.

### 3. Test the Router

```bash
# Test routing logic
python3 scripts/router.py

# Test Ollama models
ollama run qwen2.5-coder:7b "Write a Python function to calculate factorial"

# View monitoring dashboard
python3 scripts/monitor.py
```

### 4. Configure Claude Code

Update your Claude Code settings:

```bash
# Edit Claude Code settings
nano ~/.claude/settings.json
```

Add:
```json
{
  "anthropicBaseUrl": "http://localhost:3000/v1",
  "anthropicModel": "auto-route",
  "anthropicSmallFastModel": "qwen2.5-coder:7b"
}
```

## 📚 Routing Logic

### Task Categories

| Task Type | Routed To | Reasoning |
|-----------|-----------|-----------|
| File operations (read, search) | Ollama Qwen 7B | Fast local, zero cost |
| Code generation, refactoring | Ollama DeepSeek 33B | Powerful coding model, free |
| Architecture, understanding | Ollama Llama 3 70B / OpenRouter | Best reasoning |
| Security, critical decisions | Claude API | Premium quality needed |
| Large context (>32K tokens) | Claude API | 200K context window |
| Web search/fetch | Claude API | Only one with web access |

### Model Selection

```
Simple Task (complexity: low)
  ↓
  → Qwen 2.5 Coder 7B (local)
  → Fast, free, good for 80% of tasks

Medium Task (complexity: medium)
  ↓
  → DeepSeek Coder 33B (local)
  → Powerful, excellent for coding

Complex Task (complexity: high)
  ↓
  → Claude Sonnet 4 (paid)
  → Best-in-class, worth the cost
```

## 🎨 Customization

### Adding Custom Routes

Edit `config/router-config.json`:

```json
{
  "routes": [
    {
      "name": "Your Custom Route",
      "description": "Route for specific task type",
      "conditions": {
        "keywords": ["your", "keywords"],
        "complexity": "medium",
        "maxContextTokens": 4000
      },
      "target": {
        "provider": "ollama",
        "model": "your-preferred-model"
      },
      "reasoning": "Why this routing makes sense"
    }
  ]
}
```

### Available Models

**Ollama (Local - Free)**:
- `qwen2.5-coder:7b` - Fast, general coding (4GB)
- `deepseek-coder:33b` - Powerful coding (20GB)
- `llama3:70b` - Best reasoning (40GB)
- `codestral:22b` - Mistral's code model (13GB)
- `gemma2:27b` - Google's efficient model (16GB)

**OpenRouter (Free Tier)**:
- `qwen/qwen-2.5-coder-32b-instruct:free`
- `deepseek/deepseek-r1:free`
- `google/gemma-2-27b-it:free`

**Anthropic (Premium)**:
- `claude-sonnet-4-5-20250929` - Most capable
- `claude-haiku-4-5-20251001` - Fast, cheaper

### Pull Additional Models

```bash
# More models
ollama pull codestral:22b
ollama pull llama3:70b
ollama pull gemma2:27b

# List installed models
ollama list
```

## 📊 Monitoring

### Real-time Dashboard

```bash
python3 scripts/monitor.py
```

Output:
```
================================================================================
                    CLAUDE HYBRID ROUTER - DASHBOARD
================================================================================

Date: 2025-11-05 12:00:00 UTC

────────────────────────────────────────────────────────────────────────────────
OVERALL STATISTICS
────────────────────────────────────────────────────────────────────────────────
Total Requests Today:            247
Actual Cost:                   $0.85
Cost Without Router:          $18.40
💰 Total Savings:             $17.55 (95.4%)

────────────────────────────────────────────────────────────────────────────────
PROVIDER BREAKDOWN
────────────────────────────────────────────────────────────────────────────────
Provider             Requests        Cost   Avg Tokens        %
────────────────────────────────────────────────────────────────────────────────
ollama                    198       $0.00         2341     80.2%
openrouter                 37       $0.00         4128     15.0%
anthropic                  12       $0.85         8456      4.9%
```

### View Logs

```bash
# Today's request log
cat logs/requests-$(date +%Y-%m-%d).jsonl

# Live monitoring
tail -f logs/requests-$(date +%Y-%m-%d).jsonl
```

## 💰 Cost Optimization Tips

### 1. Maximize Local Usage (80%+)

Route these to Ollama:
- File operations (read, grep, glob)
- Simple code changes
- Syntax checking
- Documentation
- Test generation

### 2. Use Free Cloud Tier (10-15%)

Route to OpenRouter free tier:
- Larger context needs (but <32K)
- Backup when local is slow
- Multilingual tasks

### 3. Reserve Premium for Critical (5-10%)

Only use Claude API for:
- Security reviews
- Architecture decisions
- Performance optimization
- Production-critical bugs
- Web searches

### Expected Savings

**Example: 100 requests/day**
- Without router: 100 × $0.003 = **$3.00/day = $90/month**
- With router: 80 free + 15 free + 5 paid = **$0.15/day = $4.50/month**
- **Savings: $85.50/month (95%)**

## 🔧 Troubleshooting

### Ollama Not Starting

```bash
# Check if running
ps aux | grep ollama

# Start manually
ollama serve

# Check logs
journalctl -u ollama -f
```

### Model Not Found

```bash
# List available models
ollama list

# Pull missing model
ollama pull qwen2.5-coder:7b
```

### High API Costs

```bash
# Check routing decisions
cat logs/requests-$(date +%Y-%m-%d).jsonl | grep anthropic

# Review routing rules
cat config/router-config.json
```

## 📖 Examples

### Example 1: Daily Development Workflow

```bash
# Morning: Review code (local, free)
ollama run deepseek-coder:33b "Review this Python class..."

# Midday: Architecture question (could use OpenRouter free)
# Router automatically selects based on complexity

# Afternoon: Security audit (Claude API, worth the cost)
# Router detects "security" keyword → routes to Claude
```

### Example 2: Large Refactoring

```bash
# 1. Analyze codebase → Ollama Llama 70B (free)
# 2. Plan refactoring → Ollama DeepSeek 33B (free)
# 3. Validate plan → Claude API ($0.30)
# 4. Apply changes → Ollama DeepSeek 33B (free)
# 5. Final review → Claude API ($0.20)

# Total cost: $0.50 vs $15-20 without router
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional routing strategies
- More provider integrations
- Better cost estimation
- Performance optimizations

## 📝 License

MIT License - Use freely for personal and commercial projects

## 🔗 Links

- [Ollama](https://ollama.com) - Local LLM platform
- [OpenRouter](https://openrouter.ai) - Multi-provider LLM gateway
- [Claude API](https://anthropic.com/claude) - Anthropic's API
- [Top Open Source LLMs 2025](https://www.instaclustr.com/education/open-source-ai/top-10-open-source-llms-for-2025/)

## 📞 Support

- Issues: Check logs in `/root/claude-hybrid-router/logs/`
- Questions: Review this README
- Feature requests: Update routing rules in `config/router-config.json`

---

**Happy Coding with Hybrid Routing! 🚀**

*Save money, maintain quality, code faster.*

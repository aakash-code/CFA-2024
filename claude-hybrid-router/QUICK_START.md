# Quick Start Guide - Hybrid Approach 🚀

## ✅ What We've Built

You now have a **complete hybrid AI routing system** ready to use! Here's what's set up:

### 📁 Project Structure

```
/root/claude-hybrid-router/
├── config/
│   ├── router-config.json         # Intelligent routing rules
│   └── .env.example               # API key configuration template
├── scripts/
│   ├── router.py                  # Main routing engine
│   ├── monitor.py                 # Cost monitoring dashboard
│   └── setup.sh                   # Automated setup script
├── logs/                          # Request logs (created automatically)
├── README.md                      # Full documentation
└── QUICK_START.md                 # This file
```

### 🎯 What It Does

The hybrid router automatically routes your AI requests to the best model:

- **80% → Ollama (Local/Free)**: Simple tasks like file operations, basic coding
- **15% → OpenRouter (Free Cloud)**: Medium complexity tasks, backups
- **5% → Claude API (Premium)**: Critical tasks, security, architecture

**Expected savings: 80-95% on AI costs!**

## 🚀 Installation Steps

### On Your Local Machine / Production Environment

```bash
# 1. Navigate to the router directory
cd /root/claude-hybrid-router

# 2. Run the automated setup
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This will:
- ✅ Install Ollama
- ✅ Download recommended models (Qwen 2.5 Coder 7B, DeepSeek Coder 33B)
- ✅ Configure the router
- ✅ Test everything

### Manual Installation (if needed)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama
ollama serve &

# Pull models
ollama pull qwen2.5-coder:7b       # 3.8GB - Fast, general purpose
ollama pull deepseek-coder:33b      # 19GB - Powerful coding
ollama pull llama3:70b              # 40GB - Best reasoning (optional)
```

## ⚙️ Configuration

### 1. API Keys (Optional)

Only needed if you want cloud backup or premium features:

```bash
# Copy the example env file
cp config/.env.example config/.env

# Edit with your keys
nano config/.env
```

Add:
```bash
# OpenRouter (free tier available)
OPENROUTER_API_KEY=sk-or-v1-your-key

# Anthropic (pay per use)
ANTHROPIC_API_KEY=sk-ant-your-key
```

### 2. Configure Claude Code

Edit `~/.claude/settings.json`:

```json
{
  "anthropicBaseUrl": "http://localhost:11434/v1",
  "anthropicModel": "qwen2.5-coder:7b",
  "anthropicSmallFastModel": "qwen2.5-coder:7b"
}
```

For router-based routing (advanced):
```json
{
  "anthropicBaseUrl": "http://localhost:3000/v1",
  "anthropicModel": "auto-route"
}
```

## 🧪 Testing

### Test 1: Router Logic

```bash
cd /root/claude-hybrid-router
python3 scripts/router.py
```

Expected output:
```
================================================================================
HYBRID ROUTER TEST - Request Routing Analysis
================================================================================

Test 1: Read the README.md file...
  → Routed to: ollama/qwen2.5-coder:7b
  → Reasoning: Fast local model for simple operations, no API cost
  → Cost: $0.00 (FREE)
  → Match: ✓
```

### Test 2: Ollama Models

```bash
# Test fast model
ollama run qwen2.5-coder:7b "Write a Python hello world"

# Test powerful model
ollama run deepseek-coder:33b "Explain async/await in JavaScript"

# List installed models
ollama list
```

### Test 3: End-to-End with Claude Code

```bash
# Start a Claude Code session
claude

# Try simple tasks (should use Ollama)
> Read the README file
> Write a simple Python function

# Try complex tasks (router decides best model)
> Review this code for security issues
> Explain the system architecture
```

## 📊 Monitoring

### View Real-Time Dashboard

```bash
python3 /root/claude-hybrid-router/scripts/monitor.py
```

Shows:
- Total requests and costs
- Provider breakdown (local vs cloud vs premium)
- Cost savings vs Claude-only approach
- Monthly projections

### View Logs

```bash
# Today's requests
cat logs/requests-$(date +%Y-%m-%d).jsonl

# Live monitoring
tail -f logs/requests-$(date +%Y-%m-%d).jsonl
```

## 💰 Cost Examples

### Example: 100 Daily Requests

| Scenario | Ollama | OpenRouter | Claude API | Total Cost |
|----------|--------|------------|------------|------------|
| **Without Router** | 0 | 0 | 100 | $3.00 |
| **With Router** | 80 | 15 | 5 | $0.15 |
| **Savings** | - | - | - | **$2.85 (95%)** |

### Real Usage Pattern

Daily development session:
1. Read 20 files → Ollama → FREE
2. Write 30 functions → DeepSeek → FREE
3. Refactor 10 classes → DeepSeek → FREE
4. Architecture review → Claude API → $0.30
5. Security audit → Claude API → $0.20

**Total: $0.50/day = $15/month** instead of **$90/month**

## 🎨 Customization

### Add Your Own Routing Rules

Edit `config/router-config.json`:

```json
{
  "routes": [
    {
      "name": "My Custom Route",
      "description": "Route data science tasks to specific model",
      "conditions": {
        "keywords": ["pandas", "numpy", "data", "analysis"],
        "complexity": "medium"
      },
      "target": {
        "provider": "ollama",
        "model": "llama3:70b"
      },
      "reasoning": "Llama 3 70B excellent for data science"
    }
  ]
}
```

### Try Different Models

```bash
# Explore available models
ollama list

# Pull new models
ollama pull codestral:22b        # Mistral's code model
ollama pull gemma2:27b           # Google's efficient model

# Update router config to use them
nano config/router-config.json
```

## 🔧 Troubleshooting

### Ollama Not Found

```bash
# Check if running
ps aux | grep ollama

# Start manually
ollama serve &

# Test connection
curl http://localhost:11434/api/tags
```

### Router Not Working

```bash
# Check Python dependencies
python3 --version  # Need 3.8+

# Test router directly
python3 scripts/router.py

# Check logs
cat logs/requests-*.jsonl
```

### High Costs

```bash
# Review routing decisions
grep "anthropic" logs/requests-$(date +%Y-%m-%d).jsonl

# Check what's going to Claude API
python3 scripts/monitor.py
```

## 📚 Next Steps

### 1. Fine-Tune Routing
- Monitor which tasks go where
- Adjust complexity keywords in config
- Add custom routes for your workflow

### 2. Optimize Models
- Use smaller models for even faster responses
- Pull larger models for better quality
- Mix and match based on your needs

### 3. Scale Up
- Add more providers (Groq, Together AI, etc.)
- Implement caching for common requests
- Set up automated cost alerts

### 4. Integrate with CI/CD
- Use in GitHub Actions
- Automate code reviews
- Generate documentation

## 🎯 Recommended Workflow

### Morning (Planning)
- Code reviews → DeepSeek Coder (free)
- Read docs → Qwen 7B (free)
- Plan architecture → Llama 3 70B or Claude (depending on criticality)

### Afternoon (Development)
- Write code → DeepSeek Coder (free)
- Debug → DeepSeek Coder (free)
- Refactor → DeepSeek Coder (free)

### Evening (Review)
- Security scan → Claude API ($0.20-0.50)
- Performance review → Claude API ($0.20-0.50)
- Final validation → Claude API ($0.20-0.50)

**Daily cost: $0.60-1.50** vs **$15-25** without router

## 📞 Getting Help

1. **Read full documentation**: `cat README.md`
2. **Check configuration**: `cat config/router-config.json`
3. **View logs**: `cat logs/requests-*.jsonl`
4. **Test router**: `python3 scripts/router.py`
5. **Monitor costs**: `python3 scripts/monitor.py`

## 🎉 You're Ready!

Everything is set up and ready to use. The hybrid router will:

✅ Save you 80-95% on AI costs
✅ Maintain quality by using the right model for each task
✅ Provide full transparency with logs and monitoring
✅ Scale with your needs

Start coding and watch the savings add up! 🚀

---

**Questions?**
- Configuration: `config/router-config.json`
- Full docs: `README.md`
- Test: `python3 scripts/router.py`
- Monitor: `python3 scripts/monitor.py`

**Happy cost-efficient coding!** 💰✨

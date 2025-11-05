#!/usr/bin/env python3
"""
Claude Hybrid Router - Intelligent LLM Request Router
Routes requests to the best available model based on task complexity and cost optimization.
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('HybridRouter')


class CostTracker:
    """Tracks API costs and usage statistics"""

    def __init__(self, log_path: str):
        self.log_path = log_path
        self.daily_cost = 0.0
        self.request_count = {
            'ollama': 0,
            'openrouter': 0,
            'anthropic': 0
        }

    def log_request(self, provider: str, model: str, tokens: Dict[str, int], cost: float = 0.0):
        """Log a request and its cost"""
        self.request_count[provider] += 1
        self.daily_cost += cost

        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'provider': provider,
            'model': model,
            'tokens': tokens,
            'cost': cost,
            'daily_total': self.daily_cost
        }

        # Append to log file
        log_file = os.path.join(self.log_path, f"requests-{datetime.utcnow().date()}.jsonl")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def get_stats(self) -> Dict:
        """Get current usage statistics"""
        total_requests = sum(self.request_count.values())
        return {
            'total_requests': total_requests,
            'by_provider': self.request_count,
            'daily_cost': self.daily_cost,
            'cost_per_request': self.daily_cost / total_requests if total_requests > 0 else 0,
            'free_request_percentage': (
                (self.request_count['ollama'] + self.request_count['openrouter']) / total_requests * 100
                if total_requests > 0 else 0
            )
        }


class RequestAnalyzer:
    """Analyzes requests to determine complexity and routing"""

    def __init__(self, config: Dict):
        self.config = config

    def estimate_tokens(self, text: str) -> int:
        """Rough estimation of token count"""
        # Approximate: 1 token ≈ 4 characters
        return len(text) // 4

    def detect_complexity(self, request: Dict) -> str:
        """Determine task complexity: low, medium, or high"""
        content = request.get('message', {}).get('content', '').lower()

        # High complexity keywords
        high_keywords = ['security', 'optimize', 'architecture', 'critical', 'production',
                        'performance', 'scale', 'design pattern']

        # Medium complexity keywords
        medium_keywords = ['refactor', 'implement', 'class', 'function', 'algorithm',
                          'explain', 'understand', 'analyze']

        # Check keywords
        if any(keyword in content for keyword in high_keywords):
            return 'high'
        elif any(keyword in content for keyword in medium_keywords):
            return 'medium'
        else:
            return 'low'

    def detect_tools(self, request: Dict) -> List[str]:
        """Detect which tools are being requested"""
        content = request.get('message', {}).get('content', '')

        tools = []
        tool_patterns = {
            'Read': r'\bread\b|\bcat\b|\bview file\b',
            'Write': r'\bwrite\b|\bcreate file\b',
            'Edit': r'\bedit\b|\bmodify\b|\bchange\b',
            'Glob': r'\bfind\b|\bsearch files\b|\bglob\b',
            'Grep': r'\bgrep\b|\bsearch content\b',
            'Bash': r'\brun\b|\bexecute\b|\bcommand\b',
            'WebSearch': r'\bsearch web\b|\bgoogle\b',
            'WebFetch': r'\bfetch\b|\bdownload\b|\burl\b'
        }

        for tool, pattern in tool_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                tools.append(tool)

        return tools

    def select_route(self, request: Dict) -> Tuple[str, str, str]:
        """
        Select the best route for the request
        Returns: (provider, model, reasoning)
        """
        complexity = self.detect_complexity(request)
        tools = self.detect_tools(request)
        content = request.get('message', {}).get('content', '')
        token_count = self.estimate_tokens(content)

        logger.info(f"Analyzing request - Complexity: {complexity}, Tools: {tools}, Tokens: {token_count}")

        # Check each route in order
        for route in self.config['routes']:
            conditions = route['conditions']

            # Check complexity
            if 'complexity' in conditions and conditions['complexity'] != complexity:
                continue

            # Check tools
            if 'tools' in conditions:
                required_tools = conditions['tools']
                if not any(tool in tools for tool in required_tools):
                    continue

            # Check token limits
            if 'maxContextTokens' in conditions:
                if token_count > conditions['maxContextTokens']:
                    continue

            if 'minContextTokens' in conditions:
                if token_count < conditions['minContextTokens']:
                    continue

            # Check keywords
            if 'keywords' in conditions:
                if not any(keyword in content.lower() for keyword in conditions['keywords']):
                    continue

            # Route matched!
            target = route['target']
            return (
                target['provider'],
                target['model'],
                route.get('reasoning', 'Route matched')
            )

        # No route matched, use default
        default = self.config['defaultRoute']
        return (
            default['provider'],
            default['model'],
            default.get('reasoning', 'Default route')
        )


class HybridRouter:
    """Main router class"""

    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        log_path = self.config.get('monitoring', {}).get('logPath', '/tmp/router-logs')
        self.cost_tracker = CostTracker(log_path)
        self.analyzer = RequestAnalyzer(self.config)

        logger.info("Hybrid Router initialized")

    def route_request(self, request: Dict) -> Dict:
        """
        Route a request to the appropriate LLM
        Returns routing decision with provider, model, and metadata
        """
        provider, model, reasoning = self.analyzer.select_route(request)

        # Check if provider is enabled
        if not self.config['providers'][provider].get('enabled', True):
            logger.warning(f"Provider {provider} is disabled, using default")
            provider = self.config['defaultRoute']['provider']
            model = self.config['defaultRoute']['model']
            reasoning = "Selected provider disabled, using default"

        # Get provider config
        provider_config = self.config['providers'][provider]

        result = {
            'provider': provider,
            'model': model,
            'reasoning': reasoning,
            'base_url': provider_config['baseUrl'],
            'cost': provider_config.get('cost', 0),
            'priority': provider_config.get('priority', 999)
        }

        logger.info(f"Routing to {provider}/{model} - {reasoning}")

        return result

    def get_statistics(self) -> Dict:
        """Get router statistics"""
        stats = self.cost_tracker.get_stats()
        stats['config'] = {
            'version': self.config.get('version'),
            'providers_enabled': {
                name: config['enabled']
                for name, config in self.config['providers'].items()
            }
        }
        return stats


def main():
    """Example usage"""
    router = HybridRouter('/root/claude-hybrid-router/config/router-config.json')

    # Example requests
    test_requests = [
        {
            'message': {'content': 'Read the README.md file'},
            'expected': 'ollama/qwen2.5-coder:7b'
        },
        {
            'message': {'content': 'Implement a new authentication function with JWT'},
            'expected': 'ollama/deepseek-coder:33b'
        },
        {
            'message': {'content': 'Explain the architecture of this microservices system'},
            'expected': 'ollama/llama3:70b'
        },
        {
            'message': {'content': 'Review this code for security vulnerabilities in production'},
            'expected': 'anthropic/claude-sonnet-4'
        },
        {
            'message': {'content': 'Search the web for latest Python best practices'},
            'expected': 'anthropic/claude-sonnet-4'
        }
    ]

    print("\n" + "="*80)
    print("HYBRID ROUTER TEST - Request Routing Analysis")
    print("="*80 + "\n")

    for i, test in enumerate(test_requests, 1):
        result = router.route_request(test)
        actual = f"{result['provider']}/{result['model']}"

        print(f"Test {i}: {test['message']['content'][:60]}...")
        print(f"  → Routed to: {actual}")
        print(f"  → Reasoning: {result['reasoning']}")
        print(f"  → Cost: ${'0.00 (FREE)' if result['cost'] == 0 else result['cost']}")
        print(f"  → Expected: {test['expected']}")
        print(f"  → Match: {'✓' if actual == test['expected'] else '✗'}")
        print()

    # Print statistics
    stats = router.get_statistics()
    print("="*80)
    print("STATISTICS")
    print("="*80)
    print(f"Total Requests: {stats['total_requests']}")
    print(f"By Provider: {stats['by_provider']}")
    print(f"Free Requests: {stats['free_request_percentage']:.1f}%")
    print(f"Daily Cost: ${stats['daily_cost']:.2f}")
    print()


if __name__ == '__main__':
    main()

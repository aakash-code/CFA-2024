#!/usr/bin/env python3
"""
Claude Hybrid Router - Monitoring Dashboard
Real-time monitoring of routing decisions and cost savings
"""

import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List


class RouterMonitor:
    """Monitor router performance and cost savings"""

    def __init__(self, log_path: str = "/root/claude-hybrid-router/logs"):
        self.log_path = log_path

    def load_todays_logs(self) -> List[Dict]:
        """Load today's request logs"""
        today = datetime.utcnow().date()
        log_file = os.path.join(self.log_path, f"requests-{today}.jsonl")

        if not os.path.exists(log_file):
            return []

        logs = []
        with open(log_file, 'r') as f:
            for line in f:
                logs.append(json.loads(line))

        return logs

    def calculate_savings(self, logs: List[Dict]) -> Dict:
        """Calculate cost savings vs using Claude API for everything"""
        total_requests = len(logs)
        if total_requests == 0:
            return {
                'total_requests': 0,
                'actual_cost': 0.0,
                'without_router_cost': 0.0,
                'savings': 0.0,
                'savings_percentage': 0.0
            }

        actual_cost = sum(log['cost'] for log in logs)

        # Estimate cost if all requests went to Claude API
        # Average Claude API cost: ~$0.003 per request (estimate)
        avg_claude_cost_per_request = 0.003
        without_router_cost = total_requests * avg_claude_cost_per_request

        savings = without_router_cost - actual_cost
        savings_percentage = (savings / without_router_cost * 100) if without_router_cost > 0 else 0

        return {
            'total_requests': total_requests,
            'actual_cost': actual_cost,
            'without_router_cost': without_router_cost,
            'savings': savings,
            'savings_percentage': savings_percentage
        }

    def analyze_by_provider(self, logs: List[Dict]) -> Dict:
        """Analyze request distribution by provider"""
        by_provider = defaultdict(lambda: {'count': 0, 'cost': 0.0, 'avg_tokens': 0})

        for log in logs:
            provider = log['provider']
            by_provider[provider]['count'] += 1
            by_provider[provider]['cost'] += log.get('cost', 0.0)

            # Calculate average tokens
            tokens = log.get('tokens', {})
            total_tokens = tokens.get('input', 0) + tokens.get('output', 0)
            by_provider[provider]['avg_tokens'] += total_tokens

        # Calculate averages
        for provider, data in by_provider.items():
            if data['count'] > 0:
                data['avg_tokens'] = int(data['avg_tokens'] / data['count'])

        return dict(by_provider)

    def print_dashboard(self):
        """Print monitoring dashboard"""
        logs = self.load_todays_logs()
        savings = self.calculate_savings(logs)
        by_provider = self.analyze_by_provider(logs)

        print("\n" + "="*80)
        print(" " * 20 + "CLAUDE HYBRID ROUTER - DASHBOARD")
        print("="*80 + "\n")

        # Today's date
        print(f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")

        # Overall statistics
        print("─" * 80)
        print("OVERALL STATISTICS")
        print("─" * 80)
        print(f"Total Requests Today:        {savings['total_requests']:>6}")
        print(f"Actual Cost:                ${savings['actual_cost']:>7.2f}")
        print(f"Cost Without Router:        ${savings['without_router_cost']:>7.2f}")
        print(f"💰 Total Savings:           ${savings['savings']:>7.2f} ({savings['savings_percentage']:.1f}%)")
        print()

        # Provider breakdown
        print("─" * 80)
        print("PROVIDER BREAKDOWN")
        print("─" * 80)
        print(f"{'Provider':<20} {'Requests':>10} {'Cost':>12} {'Avg Tokens':>12} {'%':>8}")
        print("─" * 80)

        total = savings['total_requests']
        for provider in ['ollama', 'openrouter', 'anthropic']:
            if provider in by_provider:
                data = by_provider[provider]
                percentage = (data['count'] / total * 100) if total > 0 else 0
                print(f"{provider:<20} {data['count']:>10} ${data['cost']:>11.2f} "
                      f"{data['avg_tokens']:>12} {percentage:>7.1f}%")
            else:
                print(f"{provider:<20} {0:>10} ${0:>11.2f} {0:>12} {0:>7.1f}%")

        print()

        # Cost efficiency
        if total > 0:
            free_requests = by_provider.get('ollama', {}).get('count', 0) + \
                          by_provider.get('openrouter', {}).get('count', 0)
            free_percentage = (free_requests / total * 100)

            print("─" * 80)
            print("COST EFFICIENCY")
            print("─" * 80)
            print(f"Free Requests (Local/OpenRouter): {free_requests}/{total} ({free_percentage:.1f}%)")
            print(f"Paid Requests (Claude API):       {total - free_requests}/{total} ({100-free_percentage:.1f}%)")
            print(f"Average Cost per Request:         ${savings['actual_cost']/total:.4f}")
            print()

        # Recommendations
        print("─" * 80)
        print("RECOMMENDATIONS")
        print("─" * 80)

        ollama_pct = (by_provider.get('ollama', {}).get('count', 0) / total * 100) if total > 0 else 0

        if ollama_pct < 60:
            print("⚠  Consider routing more requests to Ollama for better cost savings")
        elif ollama_pct > 90:
            print("✓  Excellent use of local models! Maximum cost efficiency")
        else:
            print("✓  Good balance between cost and performance")

        anthropic_pct = (by_provider.get('anthropic', {}).get('count', 0) / total * 100) if total > 0 else 0
        if anthropic_pct > 20:
            print("⚠  High Claude API usage. Review routing rules for optimization")
        elif anthropic_pct > 0:
            print("✓  Claude API used appropriately for complex tasks")

        print()

        # Monthly projection
        if total > 0:
            daily_cost = savings['actual_cost']
            monthly_projection = daily_cost * 30
            monthly_savings = savings['savings'] * 30

            print("─" * 80)
            print("MONTHLY PROJECTION")
            print("─" * 80)
            print(f"Projected Monthly Cost:      ${monthly_projection:>7.2f}")
            print(f"Projected Monthly Savings:   ${monthly_savings:>7.2f}")
            print(f"Without Router (Monthly):    ${savings['without_router_cost'] * 30:>7.2f}")
            print()

        print("="*80 + "\n")


def main():
    monitor = RouterMonitor()
    monitor.print_dashboard()


if __name__ == '__main__':
    main()

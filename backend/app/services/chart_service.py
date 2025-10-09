"""
Chart Generation Service
Creates visualizations for reports using matplotlib
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

logger = logging.getLogger(__name__)

# Risk level colors matching your system
RISK_COLORS = {
    "Green": "#22c55e",
    "Yellow": "#eab308",
    "Orange": "#f97316",
    "Red": "#ef4444"
}

def create_risk_distribution_chart(
    data: Dict[str, int],
    output_path: str,
    language: str = "en"
) -> str:
    """
    Create a pie chart showing risk distribution
    
    Args:
        data: {"Green": count, "Yellow": count, ...}
        output_path: Path to save the chart
        language: Language for labels
        
    Returns:
        Path to saved chart
    """
    try:
        # Load translations
        from services.i18n_service import get_translation
        
        labels = []
        sizes = []
        colors = []
        
        for risk_level in ["Green", "Yellow", "Orange", "Red"]:
            if risk_level in data and data[risk_level] > 0:
                label_key = f"chart_label_{risk_level.lower()}"
                labels.append(get_translation(label_key, language))
                sizes.append(data[risk_level])
                colors.append(RISK_COLORS[risk_level])
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 6))
        
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10}
        )
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        title = get_translation("chart_title_risk_distribution", language)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Created risk distribution chart: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating risk distribution chart: {e}")
        raise


def create_trend_chart(
    dates: List[str],
    counts: Dict[str, List[int]],
    output_path: str,
    language: str = "en"
) -> str:
    """
    Create a line chart showing risk trends over time
    
    Args:
        dates: List of date labels
        counts: {"Green": [1,2,3...], "Orange": [...], ...}
        output_path: Path to save the chart
        language: Language for labels
        
    Returns:
        Path to saved chart
    """
    try:
        from services.i18n_service import get_translation
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for risk_level in ["Red", "Orange", "Yellow", "Green"]:
            if risk_level in counts:
                label_key = f"chart_label_{risk_level.lower()}"
                ax.plot(
                    dates,
                    counts[risk_level],
                    marker='o',
                    label=get_translation(label_key, language),
                    color=RISK_COLORS[risk_level],
                    linewidth=2
                )
        
        title = get_translation("chart_title_trend", language)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Date', fontsize=11)
        ax.set_ylabel('Number of Students', fontsize=11)
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Created trend chart: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating trend chart: {e}")
        raise


def create_top_reasons_chart(
    reasons: Dict[str, int],
    output_path: str,
    language: str = "en",
    top_n: int = 5
) -> str:
    """
    Create a horizontal bar chart showing top risk reasons
    
    Args:
        reasons: {"Low attendance": count, "High backlogs": count, ...}
        output_path: Path to save the chart
        language: Language for labels
        top_n: Number of top reasons to show
        
    Returns:
        Path to saved chart
    """
    try:
        from services.i18n_service import get_translation
        
        # Sort and get top N
        sorted_reasons = sorted(reasons.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        labels = [item[0] for item in sorted_reasons]
        values = [item[1] for item in sorted_reasons]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars = ax.barh(labels, values, color='#3b82f6')
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(
                width,
                bar.get_y() + bar.get_height() / 2,
                f' {int(width)}',
                ha='left',
                va='center',
                fontweight='bold'
            )
        
        title = get_translation("chart_title_top_reasons", language)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Number of Students', fontsize=11)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Created top reasons chart: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating top reasons chart: {e}")
        raise


def generate_all_charts(
    simulation_id: str,
    data: Dict[str, Any],
    language: str = "en"
) -> Dict[str, str]:
    """
    Generate all charts for a simulation
    
    Args:
        simulation_id: Unique simulation identifier
        data: Chart data including risk_distribution, trend, reasons
        language: Language for chart labels
        
    Returns:
        Dictionary of chart types to file paths
    """
    try:
        # Create charts directory
        charts_dir = Path(__file__).parent.parent / "reports" / simulation_id / "charts"
        charts_dir.mkdir(parents=True, exist_ok=True)
        
        chart_paths = {}
        
        # Risk distribution pie chart
        if "risk_distribution" in data:
            path = charts_dir / f"risk_distribution_{language}.png"
            create_risk_distribution_chart(data["risk_distribution"], str(path), language)
            chart_paths["risk_distribution"] = str(path)
        
        # Trend line chart (if historical data available)
        if "trend" in data:
            path = charts_dir / f"trend_{language}.png"
            create_trend_chart(
                data["trend"]["dates"],
                data["trend"]["counts"],
                str(path),
                language
            )
            chart_paths["trend"] = str(path)
        
        # Top reasons bar chart
        if "top_reasons" in data:
            path = charts_dir / f"top_reasons_{language}.png"
            create_top_reasons_chart(data["top_reasons"], str(path), language)
            chart_paths["top_reasons"] = str(path)
        
        logger.info(f"Generated {len(chart_paths)} charts for {simulation_id}")
        return chart_paths
        
    except Exception as e:
        logger.error(f"Error generating charts: {e}")
        return {}

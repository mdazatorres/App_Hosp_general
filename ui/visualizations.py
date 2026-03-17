"""Visualization functions for comparing data with equilibrium"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Optional


def plot_units_comparison(
        df: pd.DataFrame,
        equilibrium: Dict[str, float],
        selected_units: List[str]
):
    """
    Plot actual vs equilibrium values for selected units

    Args:
        df: DataFrame with historical data
        equilibrium: Dictionary with equilibrium values
        selected_units: List of selected units
    """
    st.subheader("📊 Historical Data vs Equilibrium")

    # Map unit names to column names
    unit_to_column = {
        "WARD": "ward_occupied_beds",
        "STEP": "stepdown_occupied_beds",
        "ICU": "ICU_occupied_beds"
    }

    # Get units that exist in both data and equilibrium
    plot_units = []
    for unit in selected_units:
        if unit in unit_to_column and unit_to_column[unit] in df.columns:
            if unit in equilibrium:
                plot_units.append(unit)

    if not plot_units:
        st.info("No matching units found for comparison")
        return

    # Create subplots
    fig = make_subplots(
        rows=len(plot_units),
        cols=1,
        subplot_titles=[f"{unit} Unit" for unit in plot_units],
        vertical_spacing=0.15
    )

    colors = {'WARD': '#4ecdc4', 'STEP': '#45b7d1', 'ICU': '#96ceb4'}

    for i, unit in enumerate(plot_units, 1):
        column = unit_to_column[unit]

        # Plot historical data
        fig.add_trace(
            go.Scatter(
                x=df.index if 'Date' not in df.columns else df['Date'],
                y=df[column],
                mode='lines',
                name=f'{unit} Historical',
                line=dict(color=colors.get(unit, '#888888'), width=2),
                showlegend=True
            ),
            row=i, col=1
        )

        # Add equilibrium line
        eq_value = equilibrium[unit]
        fig.add_trace(
            go.Scatter(
                x=[df.index[0], df.index[-1]] if 'Date' not in df.columns else [df['Date'].iloc[0],
                                                                                df['Date'].iloc[-1]],
                y=[eq_value, eq_value],
                mode='lines',
                name=f'{unit} Equilibrium',
                line=dict(color='red', width=3, dash='dash'),
                showlegend=True
            ),
            row=i, col=1
        )

        # Add horizontal line for mean of historical data
        mean_value = df[column].mean()
        fig.add_trace(
            go.Scatter(
                x=[df.index[0], df.index[-1]] if 'Date' not in df.columns else [df['Date'].iloc[0],
                                                                                df['Date'].iloc[-1]],
                y=[mean_value, mean_value],
                mode='lines',
                name=f'{unit} Mean',
                line=dict(color='green', width=2, dash='dot'),
                showlegend=True
            ),
            row=i, col=1
        )

        # Update y-axis label
        fig.update_yaxes(title_text="Patients", row=i, col=1)

    # Update layout
    fig.update_layout(
        height=300 * len(plot_units),
        title_text="Unit Occupancy: Historical vs Equilibrium",
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.05
        )
    )

    if 'Date' in df.columns:
        fig.update_xaxes(title_text="Date")

    st.plotly_chart(fig, use_container_width=True)





def plot_utilization_metrics(
        df: pd.DataFrame,
        equilibrium: Dict[str, float],
        selected_units: List[str]
):
    """
    Plot utilization metrics for each unit
    """
    st.subheader("📊 Utilization Metrics")

    metrics = []

    unit_beds_map = {
        "WARD": "ward_occupied_beds",
        "STEP": "stepdown_occupied_beds",
        "ICU": "ICU_occupied_beds"
    }

    for unit in selected_units:
        if unit in unit_beds_map and unit_beds_map[unit] in df.columns:
            beds_col = unit_beds_map[unit]
            historical_mean = df[beds_col].mean()
            historical_std = df[beds_col].std()
            eq_value = equilibrium.get(unit, 0)

            # Calculate metrics
            metrics.append({
                'Unit': unit,
                'Historical Mean': historical_mean,
                'Historical Std': historical_std,
                'Equilibrium': eq_value,
                'Difference (%)': ((eq_value - historical_mean) / historical_mean * 100) if historical_mean > 0 else 0,
                'Min': df[beds_col].min(),
                'Max': df[beds_col].max()
            })

    if metrics:
        df_metrics = pd.DataFrame(metrics)

        # Format for display
        display_df = df_metrics.copy()
        display_df['Difference (%)'] = display_df['Difference (%)'].apply(lambda x: f"{x:.1f}%")
        display_df['Historical Mean'] = display_df['Historical Mean'].apply(lambda x: f"{x:.1f}")
        display_df['Historical Std'] = display_df['Historical Std'].apply(lambda x: f"{x:.2f}")
        display_df['Equilibrium'] = display_df['Equilibrium'].apply(lambda x: f"{x:.1f}")
        display_df['Min'] = display_df['Min'].apply(lambda x: f"{x:.0f}")
        display_df['Max'] = display_df['Max'].apply(lambda x: f"{x:.0f}")

        st.dataframe(
            display_df[['Unit', 'Historical Mean', 'Historical Std', 'Equilibrium', 'Difference (%)', 'Min', 'Max']],
            use_container_width=True,
            column_config={
                "Unit": "Unit",
                "Historical Mean": "Mean Occupancy",
                "Historical Std": "Std Dev",
                "Equilibrium": "Equilibrium",
                "Difference (%)": "vs Equilibrium",
                "Min": "Min",
                "Max": "Max"
            }
        )

        # Color code the difference
        for idx, row in df_metrics.iterrows():
            diff = row['Difference (%)']
            if abs(diff) < 5:
                st.success(f"✅ {row['Unit']}: Equilibrium is close to historical mean ({diff:.1f}% difference)")
            elif diff > 5:
                st.warning(f"⚠️ {row['Unit']}: Equilibrium is {diff:.1f}% HIGHER than historical mean")
            elif diff < -5:
                st.warning(f"⚠️ {row['Unit']}: Equilibrium is {abs(diff):.1f}% LOWER than historical mean")
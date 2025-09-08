/**
 * MoMo SMS Analytics Dashboard - Chart Handler
 * 
 * Handles data fetching, chart rendering, and dashboard interactivity
 */

// Global variables
let dashboardData = null;
let charts = {};

// Color palette for charts
const colors = {
    primary: '#3498db',
    secondary: '#2ecc71',
    warning: '#f39c12',
    danger: '#e74c3c',
    info: '#9b59b6',
    success: '#27ae60',
    dark: '#34495e',
    light: '#ecf0f1'
};

const chartColors = [
    '#3498db', '#2ecc71', '#f39c12', '#e74c3c', 
    '#9b59b6', '#27ae60', '#34495e', '#1abc9c',
    '#e67e22', '#95a5a6', '#d35400', '#8e44ad'
];

/**
 * Initialize dashboard when page loads
 */
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
});

/**
 * Load dashboard data from JSON file
 */
async function loadDashboardData() {
    showLoadingState();
    
    try {
        const response = await fetch('data/processed/dashboard.json');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        dashboardData = await response.json();
        
        if (!dashboardData || !dashboardData.analytics) {
            throw new Error('Invalid dashboard data structure');
        }
        
        renderDashboard();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showErrorState(error.message);
    }
}

/**
 * Show loading state
 */
function showLoadingState() {
    document.getElementById('loadingState').classList.remove('hidden');
    document.getElementById('errorState').classList.add('hidden');
    document.getElementById('dashboardContent').classList.add('hidden');
}

/**
 * Show error state
 */
function showErrorState(errorMessage) {
    document.getElementById('loadingState').classList.add('hidden');
    document.getElementById('errorState').classList.remove('hidden');
    document.getElementById('dashboardContent').classList.add('hidden');
    document.getElementById('errorText').textContent = errorMessage;
}

/**
 * Show dashboard content
 */
function showDashboardContent() {
    document.getElementById('loadingState').classList.add('hidden');
    document.getElementById('errorState').classList.add('hidden');
    document.getElementById('dashboardContent').classList.remove('hidden');
}

/**
 * Render complete dashboard
 */
function renderDashboard() {
    showDashboardContent();
    
    updateSummaryCards();
    renderCharts();
    renderTables();
    generateInsights();
    updateLastUpdated();
}

/**
 * Update summary cards with key metrics
 */
function updateSummaryCards() {
    const analytics = dashboardData.analytics;
    
    // Total amount with formatting
    const totalAmount = formatCurrency(analytics.total_amount || 0);
    document.getElementById('totalAmount').textContent = totalAmount;
    
    // Total transactions
    const totalTransactions = formatNumber(analytics.total_transactions || 0);
    document.getElementById('totalTransactions').textContent = totalTransactions;
    
    // Average transaction
    const avgAmount = analytics.total_transactions > 0 
        ? analytics.total_amount / analytics.total_transactions 
        : 0;
    document.getElementById('avgTransaction').textContent = formatCurrency(avgAmount);
    
    // Top category
    const topCategory = analytics.by_category && analytics.by_category.length > 0
        ? analytics.by_category[0].category
        : 'N/A';
    document.getElementById('topCategory').textContent = topCategory;
}

/**
 * Render all charts
 */
function renderCharts() {
    renderCategoryChart();
    renderTypeChart();
    renderNetworkChart();
    renderTrendsChart();
}

/**
 * Render category distribution pie chart
 */
function renderCategoryChart() {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    const categoryData = dashboardData.analytics.by_category || [];
    
    if (charts.categoryChart) {
        charts.categoryChart.destroy();
    }
    
    charts.categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categoryData.map(item => item.category),
            datasets: [{
                data: categoryData.map(item => item.count),
                backgroundColor: chartColors.slice(0, categoryData.length),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${formatNumber(value)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Render transaction type chart
 */
function renderTypeChart() {
    const ctx = document.getElementById('typeChart').getContext('2d');
    const typeData = dashboardData.analytics.by_type || [];
    
    if (charts.typeChart) {
        charts.typeChart.destroy();
    }
    
    charts.typeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: typeData.map(item => item.type),
            datasets: [{
                label: 'Transaction Count',
                data: typeData.map(item => item.count),
                backgroundColor: [colors.danger, colors.success, colors.warning],
                borderColor: [colors.danger, colors.success, colors.warning],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y || 0;
                            return `${label}: ${formatNumber(value)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatNumber(value);
                        }
                    }
                }
            }
        }
    });
}

/**
 * Render network distribution chart
 */
function renderNetworkChart() {
    const ctx = document.getElementById('networkChart').getContext('2d');
    const networkData = dashboardData.analytics.by_network || [];
    
    if (charts.networkChart) {
        charts.networkChart.destroy();
    }
    
    if (networkData.length === 0) {
        ctx.font = '16px Arial';
        ctx.fillStyle = '#666';
        ctx.textAlign = 'center';
        ctx.fillText('No network data available', ctx.canvas.width / 2, ctx.canvas.height / 2);
        return;
    }
    
    charts.networkChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: networkData.map(item => item.network),
            datasets: [{
                data: networkData.map(item => item.count),
                backgroundColor: chartColors.slice(0, networkData.length),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${formatNumber(value)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Render monthly trends chart
 */
function renderTrendsChart() {
    const ctx = document.getElementById('trendsChart').getContext('2d');
    const trendsData = dashboardData.analytics.monthly_trends || [];
    
    if (charts.trendsChart) {
        charts.trendsChart.destroy();
    }
    
    // Sort by month (assuming YYYY-MM format)
    const sortedData = trendsData.sort((a, b) => a.month.localeCompare(b.month));
    
    charts.trendsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: sortedData.map(item => formatMonth(item.month)),
            datasets: [{
                label: 'Transaction Count',
                data: sortedData.map(item => item.count),
                borderColor: colors.primary,
                backgroundColor: colors.primary + '20',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }, {
                label: 'Transaction Amount (UGX)',
                data: sortedData.map(item => item.amount),
                borderColor: colors.secondary,
                backgroundColor: colors.secondary + '20',
                borderWidth: 3,
                fill: false,
                tension: 0.4,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y || 0;
                            
                            if (label.includes('Amount')) {
                                return `${label}: ${formatCurrency(value)}`;
                            } else {
                                return `${label}: ${formatNumber(value)}`;
                            }
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Month'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Transaction Count'
                    },
                    ticks: {
                        callback: function(value) {
                            return formatNumber(value);
                        }
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Amount (UGX)'
                    },
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    }
                }
            }
        }
    });
}

/**
 * Render data tables
 */
function renderTables() {
    renderCategoryTable();
    renderNetworkTable();
}

/**
 * Render category breakdown table
 */
function renderCategoryTable() {
    const tableBody = document.querySelector('#categoryTable tbody');
    const categoryData = dashboardData.analytics.by_category || [];
    const totalTransactions = dashboardData.analytics.total_transactions || 1;
    
    tableBody.innerHTML = '';
    
    categoryData.forEach(item => {
        const row = document.createElement('tr');
        const percentage = ((item.count / totalTransactions) * 100).toFixed(1);
        const avgAmount = item.count > 0 ? item.amount / item.count : 0;
        
        row.innerHTML = `
            <td><strong>${item.category}</strong></td>
            <td>${formatNumber(item.count)}</td>
            <td>${formatCurrency(item.amount)}</td>
            <td>${formatCurrency(avgAmount)}</td>
            <td>${percentage}%</td>
        `;
        
        tableBody.appendChild(row);
    });
}

/**
 * Render network statistics table
 */
function renderNetworkTable() {
    const tableBody = document.querySelector('#networkTable tbody');
    const networkData = dashboardData.analytics.by_network || [];
    const totalTransactions = networkData.reduce((sum, item) => sum + item.count, 0);
    
    tableBody.innerHTML = '';
    
    if (networkData.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="4" style="text-align: center; color: #666;">No network data available</td>';
        tableBody.appendChild(row);
        return;
    }
    
    networkData.forEach(item => {
        const row = document.createElement('tr');
        const marketShare = totalTransactions > 0 ? ((item.count / totalTransactions) * 100).toFixed(1) : 0;
        
        row.innerHTML = `
            <td><strong>${item.network}</strong></td>
            <td>${formatNumber(item.count)}</td>
            <td>${formatCurrency(item.amount)}</td>
            <td>${marketShare}%</td>
        `;
        
        tableBody.appendChild(row);
    });
}

/**
 * Generate and display insights
 */
function generateInsights() {
    generateTransactionInsights();
    generateUsageInsights();
    generateNetworkInsights();
}

/**
 * Generate transaction pattern insights
 */
function generateTransactionInsights() {
    const insights = [];
    const analytics = dashboardData.analytics;
    
    // Most popular category
    if (analytics.by_category && analytics.by_category.length > 0) {
        const topCategory = analytics.by_category[0];
        const percentage = ((topCategory.count / analytics.total_transactions) * 100).toFixed(1);
        insights.push(`${topCategory.category} transactions account for ${percentage}% of all activity`);
    }
    
    // Debit vs Credit ratio
    const debitData = analytics.by_type?.find(item => item.type === 'DEBIT');
    const creditData = analytics.by_type?.find(item => item.type === 'CREDIT');
    if (debitData && creditData) {
        const ratio = (debitData.count / creditData.count).toFixed(1);
        insights.push(`Debit to Credit transaction ratio is ${ratio}:1`);
    }
    
    // Average transaction size
    if (analytics.total_transactions > 0) {
        const avgAmount = analytics.total_amount / analytics.total_transactions;
        insights.push(`Average transaction amount is ${formatCurrency(avgAmount)}`);
    }
    
    displayInsights('transactionInsights', insights);
}

/**
 * Generate usage trend insights
 */
function generateUsageInsights() {
    const insights = [];
    const trends = dashboardData.analytics.monthly_trends || [];
    
    if (trends.length >= 2) {
        const latest = trends[0];
        const previous = trends[1];
        
        const countChange = ((latest.count - previous.count) / previous.count * 100).toFixed(1);
        const amountChange = ((latest.amount - previous.amount) / previous.amount * 100).toFixed(1);
        
        insights.push(`Transaction count ${countChange > 0 ? 'increased' : 'decreased'} by ${Math.abs(countChange)}% from last month`);
        insights.push(`Transaction value ${amountChange > 0 ? 'increased' : 'decreased'} by ${Math.abs(amountChange)}% from last month`);
    }
    
    // Peak activity month
    if (trends.length > 0) {
        const peakMonth = trends.reduce((max, current) => current.count > max.count ? current : max, trends[0]);
        insights.push(`Peak activity was in ${formatMonth(peakMonth.month)} with ${formatNumber(peakMonth.count)} transactions`);
    }
    
    displayInsights('usageInsights', insights);
}

/**
 * Generate network analysis insights
 */
function generateNetworkInsights() {
    const insights = [];
    const networks = dashboardData.analytics.by_network || [];
    
    if (networks.length === 0) {
        insights.push('Network data not available for analysis');
    } else {
        // Dominant network
        const totalTransactions = networks.reduce((sum, item) => sum + item.count, 0);
        const topNetwork = networks[0];
        const marketShare = ((topNetwork.count / totalTransactions) * 100).toFixed(1);
        insights.push(`${topNetwork.network} dominates with ${marketShare}% market share`);
        
        // Network diversity
        insights.push(`${networks.length} different networks detected in transaction data`);
        
        // Average per network
        const avgPerNetwork = totalTransactions / networks.length;
        insights.push(`Average ${formatNumber(avgPerNetwork)} transactions per network`);
    }
    
    displayInsights('networkInsights', insights);
}

/**
 * Display insights in the specified container
 */
function displayInsights(containerId, insights) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    if (insights.length === 0) {
        container.innerHTML = '<li>No insights available</li>';
        return;
    }
    
    insights.forEach(insight => {
        const li = document.createElement('li');
        li.textContent = insight;
        container.appendChild(li);
    });
}

/**
 * Update last updated timestamp
 */
function updateLastUpdated() {
    const lastUpdated = dashboardData.metadata?.generated_at;
    const element = document.getElementById('lastUpdated');
    
    if (lastUpdated) {
        const date = new Date(lastUpdated);
        element.textContent = `Last updated: ${date.toLocaleString()}`;
    } else {
        element.textContent = 'Last updated: Unknown';
    }
}

/**
 * Utility function to format currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-UG', {
        style: 'currency',
        currency: 'UGX',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount).replace('UGX', 'UGX ');
}

/**
 * Utility function to format numbers
 */
function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

/**
 * Utility function to format month
 */
function formatMonth(monthStr) {
    if (!monthStr) return monthStr;
    
    const [year, month] = monthStr.split('-');
    const date = new Date(year, month - 1);
    
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short' 
    });
}

/**
 * Refresh dashboard data
 */
function refreshDashboard() {
    // Destroy existing charts
    Object.keys(charts).forEach(chartKey => {
        if (charts[chartKey]) {
            charts[chartKey].destroy();
            charts[chartKey] = null;
        }
    });
    
    // Reload data
    loadDashboardData();
}

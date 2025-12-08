// script.js - AI Provider Sync Dashboard Functionality

class SyncDashboard {
    constructor() {
        this.dataUrl = 'sync-status.json';
        this.init();
    }

    async init() {
        await this.loadData();
        this.renderDashboard();
        this.setupEventListeners();
    }

    async loadData() {
        try {
            const response = await fetch(this.dataUrl);
            if (!response.ok) {
                throw new Error('Failed to load sync data');
            }
            this.syncData = await response.json();
        } catch (error) {
            console.error('Error loading sync data:', error);
            this.showError('Failed to load sync status data');
        }
    }

    renderDashboard() {
        if (!this.syncData) {
            this.showLoading();
            return;
        }

        this.renderStats();
        this.renderProviders();
        this.renderChart();
        this.renderSyncHistory();
        this.updateLastUpdated();
    }

    renderStats() {
        const providers = Object.keys(this.syncData);
        const totalModels = providers.reduce((sum, provider) => {
            return sum + (this.syncData[provider].models_count || 0);
        }, 0);

        document.getElementById('total-providers').textContent = providers.length;
        document.getElementById('total-models').textContent = totalModels.toLocaleString();
        
        // Find most recent sync
        const lastSync = providers.reduce((latest, provider) => {
            const syncTime = this.syncData[provider].last_sync;
            return syncTime && syncTime > latest ? syncTime : latest;
        }, '');
        
        document.getElementById('last-sync').textContent = lastSync || 'Never';
    }

    renderProviders() {
        const container = document.getElementById('providers-container');
        container.innerHTML = '';

        Object.entries(this.syncData).forEach(([provider, data]) => {
            const card = this.createProviderCard(provider, data);
            container.appendChild(card);
        });
    }

    createProviderCard(provider, data) {
        const card = document.createElement('div');
        card.className = 'provider-card';

        const status = data.last_sync ? 'active' : 'inactive';
        const statusText = data.last_sync ? 'Active' : 'Inactive';

        card.innerHTML = `
            <div class="provider-header">
                <div class="provider-name">${this.formatProviderName(provider)}</div>
                <div class="status-badge status-${status}">${statusText}</div>
            </div>
            <div class="provider-details">
                <div class="detail-item">
                    <div class="detail-label">Models</div>
                    <div class="detail-value">${data.models_count || 0}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Last Sync</div>
                    <div class="detail-value">${data.last_sync || 'Never'}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Handler</div>
                    <div class="detail-value">${data.sync_handler || 'Unknown'}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Status</div>
                    <div class="detail-value">${statusText}</div>
                </div>
            </div>
        `;

        return card;
    }

    renderChart() {
        const ctx = document.getElementById('models-chart').getContext('2d');
        
        const providers = Object.keys(this.syncData);
        const labels = providers.map(provider => this.formatProviderName(provider));
        const data = providers.map(provider => this.syncData[provider].models_count || 0);
        
        // Generate colors based on provider
        const backgroundColors = providers.map((provider, index) => {
            const hue = (index * 137.5) % 360; // Golden angle for distribution
            return `hsl(${hue}, 70%, 65%)`;
        });

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Number of Models',
                    data: data,
                    backgroundColor: backgroundColors,
                    borderColor: backgroundColors.map(color => color.replace('65%', '50%')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Models per Provider'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Models'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Providers'
                        }
                    }
                }
            }
        });
    }

    renderSyncHistory() {
        const container = document.getElementById('sync-history');
        container.innerHTML = '';

        // Create mock history for demonstration
        const history = this.generateMockHistory();
        
        history.forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            
            historyItem.innerHTML = `
                <div class="history-provider">${item.provider}</div>
                <div class="history-time">${item.time}</div>
                <div class="history-status status-${item.status}">${item.status.toUpperCase()}</div>
            `;
            
            container.appendChild(historyItem);
        });
    }

    generateMockHistory() {
        const providers = Object.keys(this.syncData);
        const statuses = ['active', 'inactive', 'error'];
        const times = ['2 hours ago', '1 day ago', '3 days ago', '1 week ago'];
        
        return providers.map(provider => ({
            provider: this.formatProviderName(provider),
            time: times[Math.floor(Math.random() * times.length)],
            status: statuses[Math.floor(Math.random() * statuses.length)]
        })).sort(() => Math.random() - 0.5).slice(0, 5);
    }

    updateLastUpdated() {
        const now = new Date();
        const formattedDate = now.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        document.getElementById('last-updated').textContent = formattedDate;
    }

    formatProviderName(provider) {
        return provider.charAt(0).toUpperCase() + provider.slice(1);
    }

    setupEventListeners() {
        document.getElementById('refresh-btn').addEventListener('click', async () => {
            await this.refreshData();
        });
    }

    async refreshData() {
        const btn = document.getElementById('refresh-btn');
        btn.disabled = true;
        btn.textContent = '🔄 Refreshing...';
        
        await this.loadData();
        this.renderDashboard();
        
        btn.disabled = false;
        btn.textContent = '🔄 Refresh';
    }

    showLoading() {
        const container = document.getElementById('providers-container');
        container.innerHTML = '<div class="loading">Loading sync data...</div>';
    }

    showError(message) {
        const container = document.getElementById('providers-container');
        container.innerHTML = `<div class="error">${message}</div>`;
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SyncDashboard();
});
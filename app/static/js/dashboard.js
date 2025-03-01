document.addEventListener('DOMContentLoaded', () => {
    const ctx = document.getElementById('rpkChart').getContext('2d');
    let chart;

    document.getElementById('filterForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const filterBtn = document.getElementById('filterBtn');
        const loading = document.getElementById('loading');
        const messageDiv = document.getElementById('message');

        filterBtn.disabled = true;
        loading.classList.remove('d-none');
        messageDiv.innerHTML = '';

        try {
            const response = await fetch('/dashboard', {
                method: 'POST',
                body: new FormData(e.target),
            });

            if (!response.ok) throw new Error(`Erro ${response.status}: ${await response.text()}`);
            const data = await response.json();

            if (data.error) {
                messageDiv.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                if (chart) chart.destroy();
                return;
            }

            const labels = data.labels || [];
            const values = data.values || [];
            const isSinglePoint = data.single_point || false;

            if (labels.length === 0) {
                messageDiv.innerHTML = `<div class="alert alert-warning">${data.message || 'Nenhum dado disponível.'}</div>`;
                if (chart) chart.destroy();
                return;
            }

            if (isSinglePoint) {
                messageDiv.innerHTML = `<div class="alert alert-info">Apenas um ponto de dados encontrado.</div>`;
            }

            if (chart) chart.destroy();

            chart = new Chart(ctx, {
                type: isSinglePoint ? 'bar' : 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'RPK (Revenue Passenger Kilometers)',
                        data: values,
                        backgroundColor: isSinglePoint ? '#FF6200' : 'rgba(255, 98, 0, 0.2)',
                        borderColor: '#FF6200',
                        borderWidth: isSinglePoint ? 0 : 2,
                        fill: !isSinglePoint,
                        pointRadius: !isSinglePoint ? 3 : 0,
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: { display: true, text: 'RPK' },
                            ticks: { callback: value => value.toLocaleString('pt-BR') }
                        },
                        x: { title: { display: true, text: 'Data (Ano-Mês)' } }
                    },
                    plugins: {
                        legend: { display: true },
                        tooltip: { callbacks: { label: ctx => `${ctx.dataset.label}: ${ctx.raw.toLocaleString('pt-BR')}` } }
                    },
                    animation: { duration: 1000, easing: 'easeInOutQuart' }
                }
            });
        } catch (error) {
            messageDiv.innerHTML = `<div class="alert alert-danger">Erro ao carregar o gráfico: ${error.message}</div>`;
            console.error('Erro:', error);
        } finally {
            loading.classList.add('d-none');
            filterBtn.disabled = false;
        }
    });
});
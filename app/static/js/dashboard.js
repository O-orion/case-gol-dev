// static/js/dashboard.js
document.addEventListener('DOMContentLoaded', () => {
    const ctx = document.getElementById('rpkChart').getContext('2d');
    let chart;

    const filterForm = document.getElementById('filterForm');

    const btnrpk= document.getElementById('btnrpk');

    const filterBtn = document.getElementById('filterBtn');
    const exportCsvBtn = document.getElementById('exportCsvBtn');
    const exportPdfBtn = document.getElementById('exportPdfBtn');
    const loading = document.getElementById('loading');
    const messageDiv = document.getElementById('message');

    filterForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        filterBtn.disabled = true;
        loading.classList.remove('d-none');
        messageDiv.innerHTML = '';

        try {
            const response = await fetch('/dashboard', {
                method: 'POST',
                body: new FormData(filterForm),
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

    exportCsvBtn.addEventListener('click', async () => {
        exportCsvBtn.disabled = true;
        loading.classList.remove('d-none');
        messageDiv.innerHTML = '';

        try {
            const response = await fetch('/export_csv', {
                method: 'POST',
                body: new FormData(filterForm),
            });

            if (!response.ok) throw new Error(`Erro ${response.status}: ${await response.text()}`);

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = response.headers.get('Content-Disposition')?.split('filename=')[1] || 'rpk_report.csv';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);

            messageDiv.innerHTML = `<div class="alert alert-success">CSV exportado com sucesso!</div>`;
        } catch (error) {
            messageDiv.innerHTML = `<div class="alert alert-danger">Erro ao exportar CSV: ${error.message}</div>`;
            console.error('Erro:', error);
        } finally {
            loading.classList.add('d-none');
            exportCsvBtn.disabled = false;
        }
    });

    exportPdfBtn.addEventListener('click', async () => {
        exportPdfBtn.disabled = true;
        loading.classList.remove('d-none');
        messageDiv.innerHTML = '';

        try {
            const response = await fetch('/export_pdf', {
                method: 'POST',
                body: new FormData(filterForm),
            });

            if (!response.ok) throw new Error(`Erro ${response.status}: ${await response.text()}`);

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = response.headers.get('Content-Disposition')?.split('filename=')[1] || 'rpk_report.pdf';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);

            messageDiv.innerHTML = `<div class="alert alert-success">PDF exportado com sucesso!</div>`;
        } catch (error) {
            messageDiv.innerHTML = `<div class="alert alert-danger">Erro ao exportar PDF: ${error.message}</div>`;
            console.error('Erro:', error);
        } finally {
            loading.classList.add('d-none');
            exportPdfBtn.disabled = false;
        }
    });

    if (btnrpk) {
        btnrpk.addEventListener('click', async (e) => {
            e.preventDefault();
            loading.classList.remove('d-none');
            messageDiv.innerHTML = '';
    
            try {
                const response = await fetch('/rpk', {
                    method: 'POST',
                    body: new FormData(filterForm),
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
                            label: 'RPK / ASK',
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
                                title: { display: true, text: 'RPK / ASK' },
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
    }
    
});
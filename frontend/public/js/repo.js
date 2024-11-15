const graphColors = [
    'rgba(255, 99, 132, 1)',
    'rgba(255, 159, 64, 1)',
    'rgba(255, 206, 86, 1)',
    'rgba(75, 192, 192, 1)',
    'rgba(54, 162, 235, 1)',
    'rgba(153, 102, 255, 1)'
]

document.addEventListener('DOMContentLoaded', () => {

    const container = document.querySelector('.container');
    const isLocal = container.getAttribute('data-is-local') === 'true';

    if (isLocal) container.style.display = 'none'; // Hide info block if isLocal

    const theaders = document.querySelectorAll('th');
    const filterInput = document.getElementById('filter-table')

    let originalData = [];
    let elements = [];
    let sorting = {
        column: null,   // index of the column
        order: 0        // 1 for ASC, -1 for DESC, 0 for no sorting
    };

    function renderTableData(data) {
        const table = document.getElementById('properties-table');
        const tbody = table.querySelector('tbody');
        tbody.innerHTML = '';
        data.forEach(element => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${element.class}</td>
                <td>${element.level}</td>
                <td>${element.numberOfInstances}</td>
            `;
            tbody.appendChild(row);
        });
    }

    async function fetchData() {
        const repoName = window.location.pathname.split('/').pop();
        const response = await fetch(`/api/results/${repoName}`);
        const data = await response.json();

        originalData = data.elements;
        elements = JSON.parse(JSON.stringify(originalData));
        renderTableData(originalData);

        const groupedByLevel = originalData.reduce((acc, element) => {
            if (acc[element.level]) {
                acc[element.level] += element.numberOfInstances;
            } else {
                acc[element.level] = element.numberOfInstances;
            }
            return acc;
        }, {});

        const levelOrder = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];

        const elementsLevels = Object.keys(groupedByLevel).sort((a, b) => {
            return levelOrder.indexOf(a) - levelOrder.indexOf(b);
        });

        const elementsInstances = Object.values(groupedByLevel);

        renderDoughnutChart(elementsLevels, elementsInstances);
        renderHistogram(elementsLevels, elementsInstances);
    }

    // Order table
    function sortTable() {
        if (sorting.column === null || sorting.order === 0) {
            renderTableData(elements);
            return;
        }

        elements.sort((a, b) => {
            const aValue = Object.values(a)[sorting.column];
            const bValue = Object.values(b)[sorting.column];

            let comparison = 0;
            if (typeof aValue === 'number' && typeof bValue === 'number') {
                comparison = aValue - bValue;
            } else {
                comparison = aValue.localeCompare(bValue);
            }

            return sorting.order * comparison;
        });

        renderTableData(elements);
    }

    function updateSortIcons() {
        theaders.forEach((header, index) => {
            const icon = header.querySelector('.sort-icon i');

            if (sorting.column === index) {
                if (sorting.order === 1) {
                    icon.classList.replace('fa-sort', 'fa-sort-up');
                    icon.classList.replace('fa-sort-down', 'fa-sort-up');
                } else if (sorting.order === -1) {
                    icon.classList.replace('fa-sort', 'fa-sort-down');
                    icon.classList.replace('fa-sort-up', 'fa-sort-down');
                }
            } else {
                icon.classList.replace('fa-sort-up', 'fa-sort');
                icon.classList.replace('fa-sort-down', 'fa-sort');
            }
        });
    }

    // Render graph with Chart.js
    function renderDoughnutChart(labels, data) {
        const ctx = document.getElementById('ringChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: graphColors,
                    borderColor: graphColors,
                    radius: "90%",
                    hoverOffset: 20,
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function (tooltipItem) {
                                return tooltipItem.label + ': ' + tooltipItem.raw + ' items';  // Formato del tooltip
                            }
                        }
                    }
                },
                onClick: (event, elements) => {
                    if (elements.length == 0) return;
                    const index = elements[0].index;
                    console.log("Click en: ", labels[index]);
                },
                onHover: (event, elements) => {
                    if (elements.length > 0) {
                        const canvas = event.native.target;
                        canvas.style.cursor = 'pointer'; 
                    }
                }
            }
        });
    }

    function renderHistogram(levels, instances) {
        const ctx = document.getElementById('histogramChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: levels,
                datasets: [{
                    label: 'Número de Instancias',
                    data: instances,
                    backgroundColor: graphColors,
                    borderColor: graphColors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true  // Aseguramos que el eje Y comienza en 0
                    }
                }
            }
        });
    }



    // Clicks on theaders for order
    theaders.forEach((header, index) => {
        header.addEventListener('click', () => {
            let newOrder = 1; // Default to ascending

            if (sorting.column === index) {
                newOrder = sorting.order === 1 ? -1 : 0; // Toggle between ASC, DESC, and no sorting
            }

            sorting = {
                column: newOrder ? index : null,
                order: newOrder
            };

            theaders.forEach(th => th.classList.remove('sort-asc', 'sort-desc'));

            if (newOrder) {
                header.classList.add(`sort-${newOrder === 1 ? 'asc' : 'desc'}`);
            }

            sortTable();
            updateSortIcons();
        });
    });

    // Filter
    filterInput.addEventListener('input', () => {
        const filterText = filterInput.value.toLowerCase();
        elements = originalData.filter(e => e.class.toLowerCase().includes(filterText));
        renderTableData(elements);
    });

    fetchData();
});

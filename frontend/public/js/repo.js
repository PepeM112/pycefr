import { toggleDarkMode, checkDarkModeOnLoad } from "./utils.js";
import { initializeFileTree } from './fileTree.js';

const theaders = document.querySelectorAll('th');
const filterInput = document.getElementById('filter-table');
const filterClass = document.querySelectorAll('.filter-level');

let originalData = [];
let elements = [];  // For filtering purposes
let sorting = {
    column: null,   // index of the column
    order: 0        // 1 for ASC, -1 for DESC, 0 for no sorting
};

let currentFilters = []

let isDarkMode = null

let doughnutChart = null;
let barChart = null;

const graphColors = {
    A1: 'rgba(255, 99, 132, 1)',
    A2: 'rgba(255, 159, 64, 1)',
    B1: 'rgba(255, 206, 86, 1)',
    B2: 'rgba(75, 192, 192, 1)',
    C1: 'rgba(54, 162, 235, 1)',
    C2: 'rgba(153, 102, 255, 1)'
}

const container = document.querySelector('.container');
const isLocal = container.getAttribute('data-is-local') === 'true';

if (isLocal) container.style.display = 'none'; // Hide info block if isLocal

async function fetchData() {
    const repoName = window.location.pathname.split('/').pop();
    const response = await fetch(`/api/results/${repoName}`);
    return await response.json();
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
function renderDoughnutChart(labels, data, refresh = true) {
    let selectedSegments = {}
    let infoColor = (isDarkMode) ? 'snow' : '#1F2937';

    const ctx = document.getElementById('ringChart').getContext('2d');

    if (doughnutChart) {
        doughnutChart.destroy();
    }

    doughnutChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: Object.values(graphColors),
                borderColor: Object.values(graphColors),
                radius: "80%",
                hoverOffset: 20,
            }]
        },
        options: {
            animation: {
                animateRotate: refresh,
            },
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: infoColor,
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (tooltipItem) {
                            return tooltipItem.label + ': ' + tooltipItem.raw + ' items';  // Formato del tooltip
                        }
                    }
                },
                datalabels: {
                    display: true,
                    color: infoColor,
                    anchor: 'end',
                    align: 'end',
                    font: {
                        size: 12,
                        weight: 'medium',
                    },
                    formatter: (value, context) => value,
                    offset: 10,
                }
            },
            onClick: (e, elements, chart) => {
                if (elements.length > 0) {
                    console.log(elements);
                    console.log("datasets: ", data.datasets);
                    const index = elements[0].index; // Índice del segmento clickeado 
                    console.log("index: ", index);
                    selectedSegments[index] = !selectedSegments[index] ?? true;

                    // Actualizar hoverOffset para reflejar el estado seleccionado
                    chart.data.datasets[0].hoverOffset = chart.data.datasets[0].data.map((_, i) =>
                        selectedSegments[i] ? 20 : 10
                    );

                    chart.update();
                }
            },
            onHover: (event, elements) => {
                if (elements.length > 0) {
                    const canvas = event.native.target;
                    canvas.style.cursor = 'pointer';
                }
            }
        },
        plugins: [ChartDataLabels],
    });
}

function renderHistogram(levels, instances, refresh = true) {
    let gridColor = (isDarkMode) ? 'rgba(255, 250, 250, 0.5)' : 'rgba(0, 0, 0, 0.2)';
    let infoColor = (isDarkMode) ? 'snow' : '#1F2937';


    const ctx = document.getElementById('histogramChart').getContext('2d');

    if (barChart) {
        barChart.destroy();
    }

    barChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: levels,
            datasets: [{
                label: 'Número de Instancias',
                barThickness: 25,
                minBarThickness: 15,
                maxBarThickness: 30,
                data: instances,
                backgroundColor: Object.values(graphColors),
                borderColor: Object.values(graphColors),
                borderWidth: 1,
                grouped: false
            }]
        },
        options: {
            animation: refresh,
            responsive: true,
            plugins: {
                legend: {
                    display: false,
                },
                datalabels: {
                    display: true,
                    color: infoColor,
                    anchor: 'end',
                    align: 'top',
                    font: {
                        size: 12,
                        weight: 'medium',
                    },
                    formatter: (value) => value
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: infoColor,
                    },
                    grid: {
                        color: gridColor,
                        lineWidth: 1,
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: infoColor,
                    },
                    grid: {
                        color: gridColor,
                        lineWidth: 1,
                    }
                }
            }
        },
        plugins: [ChartDataLabels],
    });
}

function renderFileTree(data) {
    const fileTreeData = Object.keys(data);
    initializeFileTree('.file-tree', fileTreeData);
}

function renderTableData(data) {
    data = groupAllElementsByClass(data)
    console.log(data);
    const table = document.getElementById('properties-table');
    const tbody = table.querySelector('tbody');
    tbody.innerHTML = '';
    data.forEach(element => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${element.class}</td>
            <td><span class="element-level" style="background-color: ${graphColors[element.level]}; border-radius:50%; padding: 6px">${element.level}</span></td>
            <td>${element.numberOfInstances}</td>
        `;
        tbody.appendChild(row);
    });
}

function setupLevelFilters() {
    const levelFilter = document.querySelector('.filter-level');
    const buttons = levelFilter.querySelectorAll('button');

    buttons.forEach(button => {
        const level = button.textContent.trim();
        button.style.backgroundColor = graphColors[level] ?? '#FFFFFF';

        button.addEventListener('click', () => {
            button.classList.toggle('disabled');

            if (button.classList.contains('disabled')) {
                // Remove the level from filters
                currentFilters = currentFilters.filter(activeLevel => activeLevel !== level);
            } else {
                // Add the level to filters
                currentFilters.push(level);
            }

            // Trigger table rendering based on filters
            filterTableByLevel();
        })
    });
}

function setupInstancesFilters() {
    const slider = document.querySelector('.range-slider');
    const minValueDisplay = document.getElementById('slider-value-min');
    const maxValueDisplay = document.getElementById('slider-value-max');

    noUiSlider.create(slider, {
        start: [0, 100],
        connect: true,
        behaviour: 'drag-smooth-steps-tap',
        range: {
            min: 0,
            max: 100
        },
        step: 1,
        tooltips: false,
    });

    slider.noUiSlider.on('update', (values) => {
        const minValue = parseInt(values[0], 10);
        const maxValue = parseInt(values[1], 10);

        // Actualizar valores visibles
        minValueDisplay.textContent = minValue;
        maxValueDisplay.textContent = maxValue;

        // Agregar los valores dinámicamente como atributos en los manejadores
        slider.querySelectorAll('.noUi-handle')[0].setAttribute('data-value', minValue);
        slider.querySelectorAll('.noUi-handle')[1].setAttribute('data-value', maxValue);

        // Aquí puedes agregar la lógica de filtrado si es necesario
    });

}

// Data manipulation:

function groupAllElementsByClass(data) {
    const groupedData = Object.values(data).flat().reduce((acc, item) => {
        const key = item.class;
        if (!acc[key]) {
            acc[key] = { ...item };
        } else {
            acc[key].numberOfInstances += item.numberOfInstances;
        }
        return acc;
    }, {});

    return Object.values(groupedData);
}

document.addEventListener('DOMContentLoaded', async () => {

    checkDarkModeOnLoad()
    isDarkMode = document.body.classList.contains('dark-mode');
    const darkModeButton = document.getElementById('dark-mode-toggle');

    const data = await fetchData();
    originalData = data.elements;
    const originalDataGroupedByClass = groupAllElementsByClass(originalData);
    elements = JSON.parse(JSON.stringify(originalData));

    renderTableData(originalData);

    const originalDataGroupedByLevel = groupAllElementsByClass(originalData).reduce((acc, element) => {
        if (acc[element.level]) {
            acc[element.level] += element.numberOfInstances;
        } else {
            acc[element.level] = element.numberOfInstances;
        }
        return acc;
    }, {});

    const elementsLevels = Object.keys(originalDataGroupedByLevel).sort();
    const elementsInstances = Object.values(originalDataGroupedByLevel);

    renderDoughnutChart(elementsLevels, elementsInstances);
    renderHistogram(elementsLevels, elementsInstances);
    renderFileTree(originalData);
    setupLevelFilters();
    setupInstancesFilters();

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

    filterInput.addEventListener('input', () => {
        const filterText = filterInput.value.toLowerCase();
        elements = originalDataGroupedByClass.filter(e => e.class.toLowerCase().includes(filterText));
        renderTableData(elements);
    });

    darkModeButton.addEventListener('click', () => {
        isDarkMode = !isDarkMode;
        toggleDarkMode();
        renderTableData(elements);
        renderDoughnutChart(elementsLevels, elementsInstances, false);
        renderHistogram(elementsLevels, elementsInstances, false);
    });
});

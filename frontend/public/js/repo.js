document.addEventListener('DOMContentLoaded', () => {
    
    const container = document.querySelector('.container');
    const isLocal = container.getAttribute('data-is-local') === 'true';

    if (isLocal) {
        container.style.display = 'none'; // Hide info block if isLocal
    }

    const table = document.getElementById('properties-table');
    const theaders = table.querySelectorAll('th');
    const tbody = table.querySelector('tbody');
    let elements = [];
    let originalData = [];
    let sorting = {
        column: null, // index of the column
        order: 0 // 1 for ASC, -1 for DESC, 0 for no sorting
    };

    function loadTableData(data) {
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
        elements = data.elements;
        originalData = [...elements]; // Still pointing to original data
        loadTableData(elements);
    }

    // Order table
    function sortTable() {
        if (sorting.column === null || sorting.order === 0) {
            // No sorting or sorting by none
            loadTableData(originalData);
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

        loadTableData(elements);
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

    // Clicks on header
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

    fetchData();
});

import { formatDate } from "./utils.js";   

document.addEventListener('DOMContentLoaded', () => {
    const repoList = document.getElementById('repo-list');
    const reposSummaryList = document.getElementById('repos-summary-list');

    fetch('/api/results')
        .then(response => response.json())
        .then(data => {
            console.log("data received: ", data)
            data.forEach(repo => {
                // Crear enlaces de la sidebar
                /* const repoLink = document.createElement('a');
                repoLink.href = repo.data.owner.profile_url;
                repoLink.textContent = repo.data.name;
                repoList.appendChild(repoLink); */

                const isLocal = !repo.commits;

                const repoBlock = document.createElement('div');
                repoBlock.className = 'container repos-summary-list-block';

                // Crear el bloque de la cabecera
                const repoHeader = document.createElement('div');
                repoHeader.className = 'repos-summary-list-block-header';

                const avatarImg = document.createElement('img');
                avatarImg.src = !isLocal ? repo.data.owner.avatar : '../assets/img/default_avatar.jpg';
                avatarImg.alt = !isLocal ? `${repo.data.owner.name}'s avatar` : 'avatar';
                repoHeader.appendChild(avatarImg);

                const headerText = document.createElement('div');
                const repoName = document.createElement('h3');
                repoName.textContent = !isLocal ? repo.data.name : repo.name;
                const ownerName = document.createElement('span');
                ownerName.textContent = !isLocal ? repo.data.owner.name : 'Local';

                headerText.appendChild(repoName);
                headerText.appendChild(ownerName);
                repoHeader.appendChild(headerText);

                repoBlock.appendChild(repoHeader);

                const description = document.createElement('p');
                description.textContent = !isLocal ? repo.data.description || 'No description available' : 'Repositorio local';
                description.className = 'description';
                repoBlock.appendChild(description);

                if (!isLocal) {
                    const creationDate = document.createElement('p');
                    creationDate.innerHTML = `Fecha de creación: <span>${formatDate(repo.data.createdDate)}</span>`;
                    repoBlock.appendChild(creationDate);
    
                    const lastUpdateDate = document.createElement('p');
                    lastUpdateDate.innerHTML = `Última actualización: <span>${formatDate(repo.data.lastUpdateDate)}</span>`;
                    repoBlock.appendChild(lastUpdateDate);
    
                    const commits = document.createElement('p');
                    commits.innerHTML = `Commits: <span>${repo.commits.total_commits}</span>`;
                    repoBlock.appendChild(commits);
                }

                const repoLinkMore = document.createElement('a');
                repoLinkMore.href = `/${repo.data.name + (isLocal ? "_local" : "") }`;
                repoLinkMore.className = 'glb-btn-main';
                repoLinkMore.textContent = 'Ver más';
                repoBlock.appendChild(repoLinkMore);

                reposSummaryList.appendChild(repoBlock);
            });
        })
        .catch(error => console.error('Error al cargar los repositorios:', error));
});

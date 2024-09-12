function formatDate(dateString) {
    const options = { day: '2-digit', month: '2-digit', year: 'numeric' };
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', options);
}

document.addEventListener('DOMContentLoaded', () => {
    const repoList = document.getElementById('repo-list');
    const reposSummaryList = document.getElementById('repos-summary-list');

    fetch('/results')
        .then(response => response.json())
        .then(data => {
            data.forEach(repo => {
                console.log(repo)
                // Crear enlaces de la sidebar
                const repoLink = document.createElement('a');
                repoLink.href = repo.data.owner.profile_url;
                repoLink.textContent = repo.data.name;
                repoList.appendChild(repoLink);

                const repoBlock = document.createElement('div');
                repoBlock.className = 'container repos-summary-list-block';

                // Crear el bloque de la cabecera
                const repoHeader = document.createElement('div');
                repoHeader.className = 'repos-summary-list-block-header';

                const avatarImg = document.createElement('img');
                avatarImg.src = repo.data.owner.avatar;
                avatarImg.alt = `${repo.data.owner.name}'s avatar`;
                repoHeader.appendChild(avatarImg);

                const headerText = document.createElement('div');
                const repoName = document.createElement('h3');
                repoName.textContent = repo.data.name;
                const ownerName = document.createElement('span');
                ownerName.textContent = repo.data.owner.name;

                headerText.appendChild(repoName);
                headerText.appendChild(ownerName);
                repoHeader.appendChild(headerText);

                repoBlock.appendChild(repoHeader);

                const description = document.createElement('p');
                description.textContent = repo.data.description || 'No description available';
                description.className = 'description';
                repoBlock.appendChild(description);

                const creationDate = document.createElement('p');
                creationDate.innerHTML = `Fecha de creación: <span>${formatDate(repo.data.createdDate)}</span>`;
                repoBlock.appendChild(creationDate);

                const lastUpdateDate = document.createElement('p');
                lastUpdateDate.innerHTML = `Última actualización: <span>${formatDate(repo.data.lastUpdateDate)}</span>`;
                repoBlock.appendChild(lastUpdateDate);

                const commits = document.createElement('p');
                commits.innerHTML = `Commits: <span>${repo.commits.total_commits}</span>`;
                repoBlock.appendChild(commits);

                const repoLinkMore = document.createElement('a');
                repoLinkMore.href = `/${repo.data.name}`;
                repoLinkMore.className = 'glb-btn-main';
                repoLinkMore.textContent = 'Ver más';
                repoBlock.appendChild(repoLinkMore);

                reposSummaryList.appendChild(repoBlock);
            });
        })
        .catch(error => console.error('Error al cargar los repositorios:', error));
});

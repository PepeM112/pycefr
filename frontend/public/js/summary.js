document.addEventListener('DOMContentLoaded', () => {
    const repoList = document.getElementById('repo-list');
    const reposSummaryList = document.getElementById('repos-summary-list');

    fetch('/results')
        .then(response => response.json())
        .then(data => {
            data.forEach(repo => {
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

                const repoInfo = document.createElement('p');
                repoInfo.textContent = repo.description || '';
                repoBlock.appendChild(repoInfo);

                const repoLinkMore = document.createElement('a');
                repoLinkMore.href = `/results/${repo.data.name}`;
                repoLinkMore.className = 'glb-btn-main';
                repoLinkMore.textContent = 'Ver más';
                repoBlock.appendChild(repoLinkMore);

                reposSummaryList.appendChild(repoBlock);
            });
        })
        .catch(error => console.error('Error al cargar los repositorios:', error));
});

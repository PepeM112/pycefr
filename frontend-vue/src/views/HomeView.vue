<template>
  <div class="content">
    <header>
      <h1>Resumen</h1>
    </header>
    <div class="repo-list">
      <div class="repo-wrapper" v-for="(repo, index) in reposData" :key="'repo' + index">
        <div class="container h-100">
          <div class="repo-header">
            <img
              :src="!isLocal(repo) ? repo.data.owner.avatar : '@/assets/img/default_avatar.jpg'"
              :alt="!isLocal(repo) ? `${repo.data.owner.name}'s avatar` : 'avatar'"
            />
            <div>
              <h3>
                {{ !isLocal(repo) ? repo.data.name : repo.data.name + ' (local)' }}
              </h3>
            </div>
          </div>
          <p class="description">
            {{ !isLocal(repo) ? repo.data.description || 'No description available' : 'Repositorio local' }}
          </p>

          <template v-if="!isLocal(repo)">
            <p>
              Fecha de creación:
              <span>{{ formatDate(repo.data.createdDate) }}</span>
            </p>
            <p>
              Última actualización:
              <span>{{ formatDate(repo.data.lastUpdateDate) }}</span>
            </p>
            <p>
              Commits:
              <span>{{ totalCommits(repo.commits) }}</span>
            </p>
          </template>

          <a :href="`/repo/${repo.data.name}${isLocal(repo) ? '_local' : ''}`" class="glb-btn-main">Ver más</a>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { formatDate } from '@/utils/utils';
/* import axios from 'axios'; */

const reposData = ref();

async function loadData() {
  try {
    /* const resp = await axios.get('/api/repos');
    reposData.value = resp.data; */
    reposData.value = [
      {
        data: {
          name: 'pycefr',
          url: 'https://github.com/PepeM112/pycefr',
          description: null,
          createdDate: '2024-05-02T10:26:27Z',
          lastUpdateDate: '2024-11-18T12:52:51Z',
          owner: {
            name: 'PepeM112',
            avatar: 'https://avatars.githubusercontent.com/u/129164725?v=4',
            profile_url: 'https://github.com/PepeM112',
          },
        },
        commits: [
          {
            name: 'jmatas',
            github_user: 'PepeM112',
            loc: 20162,
            commits: 81,
            total_hours: 23,
            total_files_modified: 59,
          },
          {
            name: 'PepeM112',
            github_user: 'PepeM112',
            loc: 1077,
            commits: 5,
            total_hours: 2,
            total_files_modified: 14,
          },
          {
            name: 'GitHub',
            github_user: 'anapgh',
            loc: 2663,
            commits: 19,
            total_hours: 4,
            total_files_modified: 19,
          },
          {
            name: 'anapgh',
            github_user: 'anapgh',
            loc: 21355,
            commits: 227,
            total_hours: 38,
            total_files_modified: 32,
          },
          {
            name: 'Gregorio',
            github_user: 'gregoriorobles',
            loc: 1107,
            commits: 8,
            total_hours: 2,
            total_files_modified: 8,
          },
        ],
        contributors: [
          {
            name: 'anapgh',
            avatar: 'https://avatars.githubusercontent.com/u/60195957?v=4',
            profile_url: 'https://github.com/anapgh',
            commits: 246,
          },
          {
            name: 'PepeM112',
            avatar: 'https://avatars.githubusercontent.com/u/129164725?v=4',
            profile_url: 'https://github.com/PepeM112',
            commits: 86,
          },
          {
            name: 'gregoriorobles',
            avatar: 'https://avatars.githubusercontent.com/u/842692?v=4',
            profile_url: 'https://github.com/gregoriorobles',
            commits: 8,
          },
        ],
      },
      {
        data: {
          name: 'semi-supervised-pytorch',
          url: 'https://github.com/wohlert/semi-supervised-pytorch',
          description: 'Implementations of various VAE-based semi-supervised and generative models in PyTorch',
          createdDate: '2017-09-28T09:41:18Z',
          lastUpdateDate: '2024-11-12T17:48:47Z',
          owner: {
            name: 'wohlert',
            avatar: 'https://avatars.githubusercontent.com/u/7689122?v=4',
            profile_url: 'https://github.com/wohlert',
          },
        },
        commits: [
          {
            name: 'wohlert',
            github_user: 'wohlert',
            loc: 21326,
            commits: 34,
            total_hours: 6,
            total_files_modified: 65,
          },
        ],
        contributors: [
          {
            name: 'wohlert',
            avatar: 'https://avatars.githubusercontent.com/u/7689122?v=4',
            profile_url: 'https://github.com/wohlert',
            commits: 34,
          },
        ],
      },
      {
        data: {
          name: 'semi-supervised-pytorch',
        },
      },
    ];
  } catch (error) {
    console.error('Error loading repositories:', error);
  }
}

function isLocal(repo: any) {
  return !repo.commits;
}

function totalCommits(commits: Array<{ commits: number }>) {
  return commits.reduce((acc, curr) => acc + curr.commits, 0);
}

onMounted(async () => {
  await loadData();
});
</script>
<style lang="scss" scoped>
.repo-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2em;
}

.repo-list {
  h3 {
    font-weight: 600;
    line-height: 1.75rem;
    margin: 0;
  }

  p:not(.description) {
    font-size: 0.875rem;
    font-weight: bold;
    margin: 0 0 1rem;

    span {
      font-weight: normal;
    }
  }

  a {
    position: absolute;
    right: 1rem;
    bottom: 1rem;
  }
}

p.description {
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  white-space: normal;
  overflow: hidden;
  word-break: break-word;
  text-overflow: ellipsis !important;
  line-height: 1.125rem;
  height: calc(2 * 1.125rem);
  text-overflow: ellipsis;
  font-size: 0.875rem;
  margin: 0 0 1.25rem;
}

.repo-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;

  img {
    border-radius: 50%;
    height: 48px;
    width: 48px;
  }
}
</style>

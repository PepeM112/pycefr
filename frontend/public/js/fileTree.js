// Function to build the tree structure
function buildTree(data) {
  const root = {};

  data.forEach((path) => {
      const parts = path.split("/");
      let current = root;

      parts.forEach((part) => {
          if (!current[part]) {
              current[part] = {};
          }
          current = current[part];
      });
  });

  return root;
}

// Function to create the HTML tree
function createTreeHTML(tree, isRoot = false) {
  const ul = document.createElement("ul");

  if (isRoot) {
      const rootLi = document.createElement("li");
      const rootSpan = document.createElement("span");
      rootSpan.textContent = window.location.pathname.split("/").filter(Boolean).pop() + "/" || "root";      ;
      rootSpan.classList.add("root");
      rootLi.appendChild(rootSpan);

      rootLi.appendChild(createTreeHTML(tree));
      ul.appendChild(rootLi);

      return ul;
  }

  for (const key in tree) {
      const li = document.createElement("li");
      const span = document.createElement("span");

      if (Object.keys(tree[key]).length) {
          span.textContent = `${key}/`;
          span.classList.add("folder");
          span.addEventListener("click", toggleFolder);
          li.classList.add("collapsed");
      } else {
          span.textContent = key;
          span.classList.add("file");
      }

      li.appendChild(span);

      if (Object.keys(tree[key]).length) {
          li.appendChild(createTreeHTML(tree[key]));
      }

      ul.appendChild(li);
  }

  return ul;
}

function toggleFolder(e) {
  const li = e.target.closest("li");
  li.classList.toggle("collapsed");
  li.classList.toggle("expanded");
}

function highlightPath(element) {
  document
      .querySelectorAll(".file-tree .highlighted")
      .forEach((el) => el.classList.remove("highlighted"));

  let current = element;

  while (current) {
      if (current.tagName === "LI") {
          current.classList.add("highlighted");
      }
      current = current.parentElement;
  }
}

export function initializeFileTree(containerSelector, data) {
  const container = document.querySelector(containerSelector);

  if (!container) {
      console.error(`Element with selector "${containerSelector}" not found.`);
      return;
  }

  const treeData = buildTree(data);
  container.innerHTML = ""; // Clear the container
  container.appendChild(createTreeHTML(treeData, true));

  // Listener for highlighting paths
  container.addEventListener("click", (e) => {
      if (e.target.tagName === "SPAN") {
          highlightPath(e.target.parentElement);
      }
  });
}

import type { AnalysisFilePublic } from '@/client';
import type { TreeNode } from '@/types/treeview';
import { getExtensionIcon, type FileExtension } from '@/utils/utils';

export type BuildTreeResult = {
  tree: TreeNode[];
  idPathMap: Record<number, string>;
  selectedIds: number[];
};

export function buildFileTree(fileClasses: AnalysisFilePublic[]): BuildTreeResult {
  const paths = fileClasses.map(fc => fc.filename);

  const treeSkeleton: Record<string, Record<string, unknown>> = {};

  paths.forEach(path => {
    const parts = path.split('/');
    let current: Record<string, unknown> = treeSkeleton;
    parts.forEach(part => {
      if (!current[part]) {
        current[part] = {};
      }
      current = current[part] as Record<string, unknown>;
    });
  });

  const idPathMap: Record<number, string> = {};
  const selectedIds: number[] = [];
  let id = 1;

  function fillTree(parentNode: Record<string, unknown>, currentPath: string = ''): TreeNode[] {
    return Object.keys(parentNode).map(key => {
      const child = parentNode[key] as Record<string, unknown>;
      const fullPath = currentPath ? `${currentPath}/${key}` : key;
      const hasChildren = Object.keys(child).length > 0;

      let icon = 'mdi-file-outline';
      if (!hasChildren) {
        const parts = key.split('.');
        const extension = (parts.length > 1 ? parts.pop()?.toLowerCase() : '') as FileExtension;
        icon = getExtensionIcon(extension) || 'mdi-file-outline';
      }

      const node: TreeNode = {
        id: id++,
        title: key,
        children: hasChildren ? fillTree(child, fullPath) : undefined,
        icon: hasChildren ? undefined : icon,
      };

      if (!node.children || node.children.length === 0) {
        idPathMap[node.id] = fullPath;
      }

      selectedIds.push(node.id);

      return node;
    });
  }

  const tree = fillTree(treeSkeleton);

  return { tree, idPathMap, selectedIds };
}

export function resolveSelectedPaths(selectedIds: number[], idPathMap: Record<number, string>): Set<string> {
  const paths = new Set<string>();
  selectedIds.forEach(id => {
    const path = idPathMap[id];
    if (path) paths.add(path);
  });
  return paths;
}

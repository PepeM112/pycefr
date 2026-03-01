import { ClassId, Level } from '@/client';
import type { AnalysisClassPublicWithLevel, ChartFileItem } from '@/types/analysis';
import i18n from '@/plugins/i18n';

const { t } = i18n.global;

// --- INSIGHTS ---

export function getComplexityAbstractionInsight(items: AnalysisClassPublicWithLevel[], totalInstances: number): string {
  const advancedCount = items
    .filter(it => it.level === Level.C1 || it.level === Level.C2)
    .reduce((s, it) => s + it.instances, 0);

  const advancedRatio = (advancedCount / totalInstances) * 100;

  if (advancedRatio >= 1.5) {
    return t('analysis_insight.complexity_abstraction.high', { ratio: advancedRatio.toFixed(2) });
  } else if (advancedRatio >= 0.5) {
    return t('analysis_insight.complexity_abstraction.professional', { ratio: advancedRatio.toFixed(2) });
  } else {
    return t('analysis_insight.complexity_abstraction.standard');
  }
}

export function getPythonicDensityInsight(items: AnalysisClassPublicWithLevel[]): string {
  const pyCount = items
    .filter(it =>
      [ClassId.LISTCOMP_SIMPLE, ClassId.DICTCOMP_SIMPLE, ClassId.WITH_SIMPLE, ClassId.LAMBDA_SIMPLE].includes(
        it.classId
      )
    )
    .reduce((s, it) => s + it.instances, 0);

  const forLoopsCount = items
    .filter(it => [ClassId.LOOP_FOR_SIMPLE, ClassId.LOOP_FOR_NESTED].includes(it.classId))
    .reduce((s, it) => s + it.instances, 0);

  const idiomRatio = forLoopsCount > 0 ? pyCount / forLoopsCount : 0;

  if (idiomRatio > 0.8) {
    return t('analysis_insight.pythonic_density.highly_idiomatic');
  } else if (idiomRatio > 0.3) {
    return t('analysis_insight.pythonic_density.balanced');
  } else {
    return t('analysis_insight.pythonic_density.imperative');
  }
}

export function getExceptionHandlingInsight(items: AnalysisClassPublicWithLevel[]): string {
  const exceptionBlocks = items
    .filter(it =>
      [ClassId.EXCEPTION_TRY_EXCEPT, ClassId.EXCEPTION_TRY_FINALLY, ClassId.EXCEPTION_TRY_EXCEPT_ELSE_FINALLY].includes(
        it.classId
      )
    )
    .reduce((s, it) => s + it.instances, 0);

  const functionDefs = items
    .filter(it => [ClassId.FUNCTIONDEF_SIMPLE, ClassId.FUNCTIONDEF_RECURSIVE].includes(it.classId))
    .reduce((s, it) => s + it.instances, 0);

  const errorHandlingDensity = functionDefs > 0 ? exceptionBlocks / functionDefs : 0;

  if (errorHandlingDensity > 0.4) {
    return t('analysis_insight.exception_handling.defensive');
  } else if (errorHandlingDensity > 0.1) {
    return t('analysis_insight.exception_handling.standard');
  } else {
    return t('analysis_insight.exception_handling.optimistic');
  }
}

export function getStructuralCompetenceInsight(items: AnalysisClassPublicWithLevel[]): string {
  const oopCount = items
    .filter(it =>
      [ClassId.CLASS_SIMPLE, ClassId.CLASS_INHERITED, ClassId.CLASS_INIT, ClassId.CLASS_PROPERTIES].includes(it.classId)
    )
    .reduce((s, it) => s + it.instances, 0);

  const logicCount = items
    .filter(it => [ClassId.IF_SIMPLE, ClassId.IF_EXPRESSION, ClassId.LOOP_WHILE_SIMPLE].includes(it.classId))
    .reduce((s, it) => s + it.instances, 0);

  if (oopCount > logicCount * 0.5) {
    return t('analysis_insight.structural_competence.oop');
  } else {
    return t('analysis_insight.structural_competence.procedural');
  }
}

// --- DATA HELPERS ---

export function getLevelDistributionStats(items: AnalysisClassPublicWithLevel[]) {
  const levels = [Level.A1, Level.A2, Level.B1, Level.B2, Level.C1, Level.C2];
  return levels.map(l => items.filter(it => it.level === l).reduce((s, it) => s + it.instances, 0));
}

export function getRadarStats(items: AnalysisClassPublicWithLevel[]) {
  const categories: Record<string, ClassId[]> = {
    logic: [ClassId.IF_SIMPLE, ClassId.IF_EXPRESSION],
    loops: [ClassId.LOOP_FOR_SIMPLE, ClassId.LOOP_WHILE_SIMPLE],
    data_structs: [ClassId.LIST_SIMPLE, ClassId.DICT_SIMPLE, ClassId.LISTCOMP_SIMPLE],
    oop: [ClassId.CLASS_SIMPLE, ClassId.CLASS_INHERITED],
    functions: [ClassId.FUNCTIONDEF_SIMPLE, ClassId.LAMBDA_SIMPLE],
  };

  return Object.keys(categories).map(cat =>
    items.filter(it => categories[cat].includes(it.classId)).reduce((s, it) => s + it.instances, 0)
  );
}

export function getPythonicStats(items: AnalysisClassPublicWithLevel[]) {
  const pyClasses = [ClassId.LISTCOMP_SIMPLE, ClassId.DICTCOMP_SIMPLE, ClassId.LAMBDA_SIMPLE, ClassId.WITH_SIMPLE];
  const stdClasses = [ClassId.LOOP_FOR_SIMPLE, ClassId.LOOP_FOR_NESTED, ClassId.IF_SIMPLE, ClassId.FILE_OPEN];

  const pyCount = items.filter(it => pyClasses.includes(it.classId)).reduce((s, it) => s + it.instances, 0);
  const stdCount = items.filter(it => stdClasses.includes(it.classId)).reduce((s, it) => s + it.instances, 0);

  return [stdCount, pyCount];
}

export function getExceptionStats(items: AnalysisClassPublicWithLevel[]) {
  const catching = [
    ClassId.EXCEPTION_TRY_EXCEPT,
    ClassId.EXCEPTION_TRY_EXCEPT_ELSE_FINALLY,
    ClassId.EXCEPTION_TRY_FINALLY,
  ];
  const signaling = [ClassId.EXCEPTION_RAISE, ClassId.EXCEPTION_ASSERT];

  const catchingCount = items.filter(it => catching.includes(it.classId)).reduce((s, it) => s + it.instances, 0);
  const signalingCount = items.filter(it => signaling.includes(it.classId)).reduce((s, it) => s + it.instances, 0);

  return [catchingCount, signalingCount];
}

export function getTopPatterns(items: AnalysisClassPublicWithLevel[]) {
  return [...items].sort((a, b) => b.instances - a.instances).slice(0, 10);
}

export function getTreemapFlatData(files: ChartFileItem[]) {
  const groups: Record<string, number> = {};

  files.forEach(f => {
    const parts = f.fullPath.split('/');
    const folder = parts.length > 1 ? '/' + parts.slice(0, -1).join('/') : '/';
    groups[folder] = (groups[folder] || 0) + f.instances;
  });

  return Object.entries(groups).map(([name, value]) => ({
    g: name,
    v: value,
  }));
}

export function getTreemapBackgroundColor(ratio: number): string {
  if (ratio > 0.85) return '#BF360C';
  if (ratio > 0.65) return '#E64A19';
  if (ratio > 0.45) return '#FF8A65';
  if (ratio > 0.25) return '#FFAB91';
  return '#FFCCBC';
}

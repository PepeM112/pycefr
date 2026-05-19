import { ClassId, Level, type AnalysisFilePublic, type RepoCommitPublic } from '@/client';
import type { AnalysisClassPublicWithLevel, ChartCommitItem, ChartData, ChartFileItem } from '@/types/analysis';
import i18n from '@/plugins/i18n';

const { t } = i18n.global;

function sumInstances(items: AnalysisClassPublicWithLevel[], classIds: ClassId[]): number {
  return items.filter(it => classIds.includes(it.classId)).reduce((s, it) => s + it.instances, 0);
}

// --- INSIGHTS ---

export function getComplexityAbstractionInsight(items: AnalysisClassPublicWithLevel[], totalInstances: number): string {
  const advancedCount = items
    .filter(it => it.level === Level.C1 || it.level === Level.C2)
    .reduce((s, it) => s + it.instances, 0);

  const advancedRatio = (advancedCount / totalInstances) * 100;

  /** * HIGH ABSTRACTION THRESHOLD (>= 0.20%)
   * Found in "meta-frameworks" and tools that extend Python's core behavior.
   * Benchmarks: FastAPI (0.31%), Six (0.31%), Pydantic (0.21%), SQLAlchemy (0.20%).
   * Characterized by heavy use of metaclasses, dynamic attribute access, and custom descriptors.
   */
  if (advancedRatio >= 0.2) {
    return t('analysis_insight.complexity_abstraction.high', { ratio: advancedRatio.toFixed(2) });
  } else if (advancedRatio >= 0.05) {
    /** * PROFESSIONAL CODEBASE THRESHOLD (>= 0.05%)
     * Found in high-quality libraries and mature backend services.
     * Benchmark: Loguru (0.06%).
     * Indicates solid use of advanced patterns like decorators, generators,
     * and complex type hinting without over-engineering.
     */
    return t('analysis_insight.complexity_abstraction.professional', { ratio: advancedRatio.toFixed(2) });
  } else {
    /** * STANDARD STRUCTURAL THRESHOLD (< 0.05%)
     * Found in most application-level code, business logic, and scripts.
     * Benchmarks: Django Apps (0.04%), Tenacity, Requests.
     * Focuses on readability and execution flow over deep structural abstractions.
     */
    return t('analysis_insight.complexity_abstraction.standard');
  }
}

export function getPythonicDensityInsight(items: AnalysisClassPublicWithLevel[]): string {
  const pyCount = sumInstances(items, [ClassId.LISTCOMP_SIMPLE, ClassId.DICTCOMP_SIMPLE, ClassId.WITH_SIMPLE, ClassId.LAMBDA_SIMPLE]);
  const forLoopsCount = sumInstances(items, [ClassId.LOOP_FOR_SIMPLE, ClassId.LOOP_FOR_NESTED]);

  const idiomRatio = forLoopsCount > 0 ? pyCount / forLoopsCount : 0;

  /**
   * HIGHLY IDIOMATIC THRESHOLD (>= 3.5)
   * There are 3.5x more comprehensions/context managers than standard for-loops.
   * This indicates a developer/team that actively refactors loops into pythonic structures.
   */
  if (idiomRatio >= 3.5) {
    return t('analysis_insight.pythonic_density.highly_idiomatic');
  } else if (idiomRatio >= 1.5) {
    /**
     * BALANCED THRESHOLD (>= 1.5)
     * Roughly equal use of loops and pythonic constructs.
     * Typical of modern, well-maintained libraries.
     */
    return t('analysis_insight.pythonic_density.balanced');
  } else {
    /**
     * IMPERATIVE THRESHOLD (< 1.5)
     * Heavy reliance on traditional iteration.
     */
    return t('analysis_insight.pythonic_density.imperative');
  }
}

export function getExceptionHandlingInsight(items: AnalysisClassPublicWithLevel[]): string {
  const exceptionBlocks = sumInstances(items, [ClassId.EXCEPTION_TRY_EXCEPT, ClassId.EXCEPTION_TRY_FINALLY, ClassId.EXCEPTION_TRY_EXCEPT_ELSE_FINALLY]);
  const functionDefs = sumInstances(items, [ClassId.FUNCTIONDEF_SIMPLE, ClassId.FUNCTIONDEF_RECURSIVE]);

  const errorHandlingDensity = functionDefs > 0 ? exceptionBlocks / functionDefs : 0;
  /**
   * DEFENSIVE THRESHOLD (>= 0.15)
   * 1.5 try-blocks per 10 functions.
   * Found in network/I-O heavy libraries (like Requests) that must handle low-level failures constantly.
   */
  if (errorHandlingDensity >= 0.15) {
    return t('analysis_insight.exception_handling.defensive');
  } else if (errorHandlingDensity >= 0.05) {
    /**
     * STANDARD THRESHOLD (>= 0.05)
     * 1 try-block per 20 functions.
     * Normal application logic. Exceptions are caught at strategic boundaries.
     */
    return t('analysis_insight.exception_handling.standard');
  } else {
    /**
     * OPTIMISTIC THRESHOLD (< 0.05)
     * Relies heavily on framework-level middleware (like Django/FastAPI) or global error handlers.
     */
    return t('analysis_insight.exception_handling.optimistic');
  }
}

export function getStructuralCompetenceInsight(items: AnalysisClassPublicWithLevel[]): string {
  const oopCount = sumInstances(items, [ClassId.CLASS_SIMPLE, ClassId.CLASS_INHERITED, ClassId.CLASS_INIT, ClassId.CLASS_PROPERTIES]);
  const proceduralCount = sumInstances(items, [ClassId.FUNCTIONDEF_SIMPLE]);

  // If there are no functions, it's heavily OOP.
  const structureRatio = proceduralCount > 0 ? oopCount / proceduralCount : 10;
  /**
   * OOP FOCUS (>= 0.3)
   * High ratio of classes/init blocks compared to standalone functions.
   * Frameworks like Django and FastAPI live here.
   */
  if (structureRatio >= 0.3) {
    return t('analysis_insight.structural_competence.oop');
  } else {
    /**
     * PROCEDURAL/LOGIC FOCUS (< 0.3)
     * Heavy reliance on standalone functions and flat architecture.
     * Libraries like Loguru or specific data-processing scripts live here.
     */
    return t('analysis_insight.structural_competence.procedural');
  }
}

// --- CHART DATA BUILDERS ---

function buildChartFiles(
  fileClasses: AnalysisFilePublic[],
  selectedFilePaths: Set<string>
): ChartFileItem[] {
  const hasSelection = selectedFilePaths.size > 0;

  return fileClasses
    .filter(f => (hasSelection ? selectedFilePaths.has(f.filename) : true))
    .map(f => ({
      name: f.filename.split('/').pop() || f.filename,
      fullPath: f.filename,
      instances: f.classes?.reduce((acc, c) => acc + c.instances, 0) || 0,
    }))
    .sort((a, b) => b.instances - a.instances)
    .slice(0, 10);
}

function buildChartCommits(commits: RepoCommitPublic[]): ChartCommitItem[] {
  return commits.map(c => ({
    hash: c.githubUser || c.username || 'unknown',
    filesCount: c.totalFilesModified,
    complexity: c.loc,
  }));
}

export function buildChartData(
  fileClasses: AnalysisFilePublic[],
  commits: RepoCommitPublic[],
  selectedFilePaths: Set<string>,
  tableItems: AnalysisClassPublicWithLevel[]
): ChartData {
  return {
    items: tableItems,
    files: buildChartFiles(fileClasses, selectedFilePaths),
    commits: buildChartCommits(commits),
  };
}

// --- DATA HELPERS ---

export function getLevelDistributionStats(items: AnalysisClassPublicWithLevel[]) {
  const levels = [Level.A1, Level.A2, Level.B1, Level.B2, Level.C1, Level.C2];
  return levels.map(l => items.filter(it => it.level === l).reduce((s, it) => s + it.instances, 0));
}

export function getRadarStats(items: AnalysisClassPublicWithLevel[]) {
  const categories: ClassId[][] = [
    [ClassId.IF_SIMPLE, ClassId.IF_EXPRESSION],
    [ClassId.LOOP_FOR_SIMPLE, ClassId.LOOP_WHILE_SIMPLE],
    [ClassId.LIST_SIMPLE, ClassId.DICT_SIMPLE, ClassId.LISTCOMP_SIMPLE],
    [ClassId.CLASS_SIMPLE, ClassId.CLASS_INHERITED],
    [ClassId.FUNCTIONDEF_SIMPLE, ClassId.LAMBDA_SIMPLE],
  ];

  return categories.map(ids => sumInstances(items, ids));
}

export function getPythonicStats(items: AnalysisClassPublicWithLevel[]) {
  const pyClasses = [ClassId.LISTCOMP_SIMPLE, ClassId.DICTCOMP_SIMPLE, ClassId.LAMBDA_SIMPLE, ClassId.WITH_SIMPLE];
  const stdClasses = [ClassId.LOOP_FOR_SIMPLE, ClassId.LOOP_FOR_NESTED, ClassId.IF_SIMPLE, ClassId.FILE_OPEN];

  return [sumInstances(items, stdClasses), sumInstances(items, pyClasses)];
}

export function getExceptionStats(items: AnalysisClassPublicWithLevel[]) {
  const catching = [ClassId.EXCEPTION_TRY_EXCEPT, ClassId.EXCEPTION_TRY_EXCEPT_ELSE_FINALLY, ClassId.EXCEPTION_TRY_FINALLY];
  const signaling = [ClassId.EXCEPTION_RAISE, ClassId.EXCEPTION_ASSERT];

  return [sumInstances(items, catching), sumInstances(items, signaling)];
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

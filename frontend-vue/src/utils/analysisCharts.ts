import { ClassId, Level, type AnalysisFilePublic, type RepoCommitPublic } from '@/client';
import type { AnalysisClassPublicWithLevel, ChartCommitItem, ChartData, ChartFileItem } from '@/types/analysis';

type TranslateFn = (key: string) => string;

function sumInstances(items: AnalysisClassPublicWithLevel[], classIds: ClassId[]): number {
  return items.filter(it => classIds.includes(it.classId)).reduce((s, it) => s + it.instances, 0);
}

// --- INSIGHT THRESHOLDS ---
// Calibrated against: Django, SQLAlchemy, Six, Loguru, Tenacity (May 2026)

/**
 * Complexity & Abstraction — % of C1/C2 instances over total.
 * HIGH (>= 0.15%): Meta-frameworks that extend Python's core behavior.
 *   Benchmarks: Six (0.31%), SQLAlchemy (0.19%).
 *   Characterized by metaclasses, descriptors, and dynamic attribute creation.
 * PROFESSIONAL (>= 0.03%): Mature libraries with selective advanced patterns.
 *   Benchmarks: Loguru (0.06%), Django (0.04%).
 *   Solid OOP/functional patterns, decorators, generators — without over-engineering.
 * STANDARD (< 0.03%): Application-level code, business logic, scripts.
 *   Benchmarks: Tenacity (0.00%).
 *   Straightforward execution flow over deep abstractions.
 */
const COMPLEXITY_HIGH = 0.15;
const COMPLEXITY_PROFESSIONAL = 0.03;

/**
 * Pythonic Density — ratio of comprehensions/context-managers/lambdas to for-loops.
 * HIGHLY IDIOMATIC (>= 5.0): Pythonic constructs significantly outnumber loops.
 *   Benchmarks: Loguru (6.55).
 *   Indicates active refactoring of loops into expressive one-liners.
 * BALANCED (>= 2.0): Healthy mix of both styles.
 *   Benchmarks: Django (4.58), SQLAlchemy (3.61), Tenacity (3.29).
 * IMPERATIVE (< 2.0): Traditional for-loops dominate.
 *   Benchmarks: Six (1.91).
 *   Explicit step-by-step iteration preferred over shorthands.
 */
const PYTHONIC_HIGHLY_IDIOMATIC = 5.0;
const PYTHONIC_BALANCED = 2.0;

/**
 * Exception Handling — try-except blocks per function definition.
 * DEFENSIVE (>= 0.15): ~1.5 try-blocks per 10 functions.
 *   Found in I/O-heavy or network-facing code (e.g. Requests, Six compat shims).
 *   Benchmarks: Six (0.15), Loguru (0.12).
 * STANDARD (>= 0.05): ~1 try-block per 20 functions.
 *   Exceptions caught at strategic boundaries.
 *   Benchmarks: Tenacity (0.08).
 * OPTIMISTIC (< 0.05): Relies on centralized/framework-level error management.
 *   Benchmarks: Django (0.04), SQLAlchemy (0.02).
 */
const ERROR_DEFENSIVE = 0.15;
const ERROR_STANDARD = 0.05;

/**
 * Structural Competence — OOP constructs (classes) per standalone function.
 * OOP FOCUS (>= 0.3): Class-heavy architecture.
 *   Benchmarks: Six (0.53), Django (0.44), SQLAlchemy (0.39), Tenacity (0.37).
 * PROCEDURAL (< 0.3): Flat architecture driven by standalone functions.
 *   Benchmarks: Loguru (0.08).
 */
const STRUCTURE_OOP = 0.3;

// --- INSIGHTS ---

export function getComplexityAbstractionInsight(
  items: AnalysisClassPublicWithLevel[],
  totalInstances: number,
  t: TranslateFn
): string {
  const advancedCount = items
    .filter(it => it.level === Level.C1 || it.level === Level.C2)
    .reduce((s, it) => s + it.instances, 0);

  if (totalInstances === 0) return t('analysis_insight.complexity_abstraction.standard');

  const advancedRatio = (advancedCount / totalInstances) * 100;

  if (advancedRatio >= COMPLEXITY_HIGH) return t('analysis_insight.complexity_abstraction.high');
  if (advancedRatio >= COMPLEXITY_PROFESSIONAL) return t('analysis_insight.complexity_abstraction.professional');
  return t('analysis_insight.complexity_abstraction.standard');
}

export function getPythonicDensityInsight(items: AnalysisClassPublicWithLevel[], t: TranslateFn): string {
  const pyCount = sumInstances(items, [
    ClassId.LISTCOMP_SIMPLE,
    ClassId.DICTCOMP_SIMPLE,
    ClassId.WITH_SIMPLE,
    ClassId.LAMBDA_SIMPLE,
  ]);
  const forLoopsCount = sumInstances(items, [ClassId.LOOP_FOR_SIMPLE, ClassId.LOOP_FOR_NESTED]);

  const idiomRatio = forLoopsCount > 0 ? pyCount / forLoopsCount : 0;

  if (idiomRatio >= PYTHONIC_HIGHLY_IDIOMATIC) return t('analysis_insight.pythonic_density.highly_idiomatic');
  if (idiomRatio >= PYTHONIC_BALANCED) return t('analysis_insight.pythonic_density.balanced');
  return t('analysis_insight.pythonic_density.imperative');
}

export function getExceptionHandlingInsight(items: AnalysisClassPublicWithLevel[], t: TranslateFn): string {
  const exceptionBlocks = sumInstances(items, [
    ClassId.EXCEPTION_TRY_EXCEPT,
    ClassId.EXCEPTION_TRY_FINALLY,
    ClassId.EXCEPTION_TRY_EXCEPT_ELSE_FINALLY,
  ]);
  const functionDefs = sumInstances(items, [ClassId.FUNCTIONDEF_SIMPLE, ClassId.FUNCTIONDEF_RECURSIVE]);

  const errorHandlingDensity = functionDefs > 0 ? exceptionBlocks / functionDefs : 0;

  if (errorHandlingDensity >= ERROR_DEFENSIVE) return t('analysis_insight.exception_handling.defensive');
  if (errorHandlingDensity >= ERROR_STANDARD) return t('analysis_insight.exception_handling.standard');
  return t('analysis_insight.exception_handling.optimistic');
}

export function getStructuralCompetenceInsight(items: AnalysisClassPublicWithLevel[], t: TranslateFn): string {
  const oopCount = sumInstances(items, [
    ClassId.CLASS_SIMPLE,
    ClassId.CLASS_INHERITED,
    ClassId.CLASS_INIT,
    ClassId.CLASS_PROPERTIES,
  ]);
  const proceduralCount = sumInstances(items, [ClassId.FUNCTIONDEF_SIMPLE]);

  const structureRatio = proceduralCount > 0 ? oopCount / proceduralCount : 10;

  if (structureRatio >= STRUCTURE_OOP) return t('analysis_insight.structural_competence.oop');
  return t('analysis_insight.structural_competence.procedural');
}

// --- CHART DATA BUILDERS ---

function buildChartFiles(fileClasses: AnalysisFilePublic[], selectedFilePaths: Set<string>): ChartFileItem[] {
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
  const catching = [
    ClassId.EXCEPTION_TRY_EXCEPT,
    ClassId.EXCEPTION_TRY_EXCEPT_ELSE_FINALLY,
    ClassId.EXCEPTION_TRY_FINALLY,
  ];
  const signaling = [ClassId.EXCEPTION_RAISE, ClassId.EXCEPTION_ASSERT];

  return [sumInstances(items, catching), sumInstances(items, signaling)];
}

export function getTopPatterns(items: AnalysisClassPublicWithLevel[]) {
  return [...items].sort((a, b) => b.instances - a.instances).slice(0, 10);
}

export function getTreemapFlatData(files: ChartFileItem[]) {
  const groups = files.reduce<Record<string, number>>((acc, f) => {
    const parts = f.fullPath.split('/');
    const folder = parts.length > 1 ? '/' + parts.slice(0, -1).join('/') : '/';
    acc[folder] = (acc[folder] || 0) + f.instances;
    return acc;
  }, {});

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

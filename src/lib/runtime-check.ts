/**
 * 运行时环境检查工具
 */

/**
 * 检查是否在Edge Runtime环境中运行
 */
export function isEdgeRuntime(): boolean {
  // 在Edge Runtime中，process 对象不存在或者 process.versions.node 不存在
  return typeof process === 'undefined' || !process.versions?.node;
}

/**
 * 检查是否在生产环境中运行
 */
export function isProduction(): boolean {
  return process.env.NODE_ENV === 'production';
}

/**
 * 检查是否支持文件系统操作
 */
export function supportsFileSystem(): boolean {
  try {
    // 在Edge Runtime中，fs模块不可用
    return typeof require !== 'undefined' && !isEdgeRuntime();
  } catch {
    return false;
  }
} 
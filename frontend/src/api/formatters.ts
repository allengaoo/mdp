/**
 * 数据格式化工具函数
 */

/**
 * 格式化日期字符串为本地化格式
 * @param dateString ISO 日期字符串
 * @returns 格式化的日期字符串
 */
export function formatDate(dateString: string | null | undefined): string {
  if (!dateString) return '未知';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return dateString;
    }
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateString;
  }
}

/**
 * 格式化文件大小
 * @param bytes 字节数
 * @returns 格式化的文件大小字符串
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  if (bytes < 0) return 'Invalid';
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const k = 1024;
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const size = bytes / Math.pow(k, i);
  
  return `${size.toFixed(i > 0 ? 2 : 0)} ${units[i]}`;
}

/**
 * 截断长文本
 * @param text 原始文本
 * @param maxLength 最大长度
 * @param suffix 截断后缀
 * @returns 截断后的文本
 */
export function truncateText(
  text: string | null | undefined,
  maxLength: number,
  suffix: string = '...'
): string {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - suffix.length) + suffix;
}

/**
 * 将 snake_case 转换为 Title Case
 * @param str snake_case 字符串
 * @returns Title Case 字符串
 */
export function snakeToTitleCase(str: string): string {
  if (!str) return '';
  return str
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

/**
 * 将 camelCase 转换为 Title Case
 * @param str camelCase 字符串
 * @returns Title Case 字符串
 */
export function camelToTitleCase(str: string): string {
  if (!str) return '';
  return str
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, (s) => s.toUpperCase())
    .trim();
}

/**
 * 生成随机 ID
 * @param prefix ID 前缀
 * @param length 随机部分长度
 * @returns 随机 ID
 */
export function generateId(prefix: string = '', length: number = 8): string {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return prefix ? `${prefix}-${result}` : result;
}

/**
 * 判断对象是否为空
 * @param obj 要检查的对象
 * @returns 是否为空
 */
export function isEmpty(obj: any): boolean {
  if (obj === null || obj === undefined) return true;
  if (typeof obj === 'string') return obj.trim().length === 0;
  if (Array.isArray(obj)) return obj.length === 0;
  if (typeof obj === 'object') return Object.keys(obj).length === 0;
  return false;
}

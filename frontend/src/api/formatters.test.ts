/**
 * 单元测试: 数据格式化工具函数
 */
import { describe, it, expect } from 'vitest';
import {
  formatDate,
  formatFileSize,
  truncateText,
  snakeToTitleCase,
  camelToTitleCase,
  generateId,
  isEmpty,
} from './formatters';

describe('formatters', () => {
  describe('formatDate', () => {
    it('应该格式化有效的日期字符串', () => {
      const result = formatDate('2024-06-15T14:30:00Z');
      // 验证包含年月日（具体格式取决于 locale）
      expect(result).toMatch(/2024/);
    });

    it('应该在日期为 null 时返回"未知"', () => {
      expect(formatDate(null)).toBe('未知');
    });

    it('应该在日期为 undefined 时返回"未知"', () => {
      expect(formatDate(undefined)).toBe('未知');
    });

    it('应该在日期为空字符串时返回"未知"', () => {
      expect(formatDate('')).toBe('未知');
    });

    it('应该在日期无效时返回原始字符串', () => {
      expect(formatDate('invalid-date')).toBe('invalid-date');
    });
  });

  describe('formatFileSize', () => {
    it('应该正确格式化字节', () => {
      expect(formatFileSize(0)).toBe('0 B');
      expect(formatFileSize(100)).toBe('100 B');
      expect(formatFileSize(1023)).toBe('1023 B');
    });

    it('应该正确格式化 KB', () => {
      expect(formatFileSize(1024)).toBe('1.00 KB');
      expect(formatFileSize(1536)).toBe('1.50 KB');
    });

    it('应该正确格式化 MB', () => {
      expect(formatFileSize(1024 * 1024)).toBe('1.00 MB');
      expect(formatFileSize(1.5 * 1024 * 1024)).toBe('1.50 MB');
    });

    it('应该正确格式化 GB', () => {
      expect(formatFileSize(1024 * 1024 * 1024)).toBe('1.00 GB');
    });

    it('应该处理负数', () => {
      expect(formatFileSize(-1)).toBe('Invalid');
    });
  });

  describe('truncateText', () => {
    it('应该截断超过最大长度的文本', () => {
      expect(truncateText('Hello World', 8)).toBe('Hello...');
    });

    it('应该不截断短于最大长度的文本', () => {
      expect(truncateText('Hello', 10)).toBe('Hello');
    });

    it('应该处理自定义后缀', () => {
      expect(truncateText('Hello World', 8, '…')).toBe('Hello W…');
    });

    it('应该处理 null', () => {
      expect(truncateText(null, 10)).toBe('');
    });

    it('应该处理 undefined', () => {
      expect(truncateText(undefined, 10)).toBe('');
    });

    it('应该处理空字符串', () => {
      expect(truncateText('', 10)).toBe('');
    });

    it('应该处理刚好等于最大长度的文本', () => {
      expect(truncateText('Hello', 5)).toBe('Hello');
    });
  });

  describe('snakeToTitleCase', () => {
    it('应该将 snake_case 转换为 Title Case', () => {
      expect(snakeToTitleCase('hello_world')).toBe('Hello World');
      expect(snakeToTitleCase('user_first_name')).toBe('User First Name');
    });

    it('应该处理单个单词', () => {
      expect(snakeToTitleCase('hello')).toBe('Hello');
    });

    it('应该处理空字符串', () => {
      expect(snakeToTitleCase('')).toBe('');
    });

    it('应该处理大写字母', () => {
      expect(snakeToTitleCase('HELLO_WORLD')).toBe('Hello World');
    });
  });

  describe('camelToTitleCase', () => {
    it('应该将 camelCase 转换为 Title Case', () => {
      expect(camelToTitleCase('helloWorld')).toBe('Hello World');
      expect(camelToTitleCase('userFirstName')).toBe('User First Name');
    });

    it('应该处理首字母大写', () => {
      expect(camelToTitleCase('HelloWorld')).toBe('Hello World');
    });

    it('应该处理单个单词', () => {
      expect(camelToTitleCase('hello')).toBe('Hello');
    });

    it('应该处理空字符串', () => {
      expect(camelToTitleCase('')).toBe('');
    });
  });

  describe('generateId', () => {
    it('应该生成指定长度的 ID', () => {
      const id = generateId('', 8);
      expect(id).toHaveLength(8);
    });

    it('应该添加前缀', () => {
      const id = generateId('user', 8);
      expect(id).toMatch(/^user-[a-z0-9]{8}$/);
    });

    it('应该生成随机 ID', () => {
      const id1 = generateId('test', 8);
      const id2 = generateId('test', 8);
      // 两个 ID 应该不同（极小概率相同）
      expect(id1).not.toBe(id2);
    });

    it('应该只包含小写字母和数字', () => {
      const id = generateId('', 100);
      expect(id).toMatch(/^[a-z0-9]+$/);
    });
  });

  describe('isEmpty', () => {
    it('应该判断 null 为空', () => {
      expect(isEmpty(null)).toBe(true);
    });

    it('应该判断 undefined 为空', () => {
      expect(isEmpty(undefined)).toBe(true);
    });

    it('应该判断空字符串为空', () => {
      expect(isEmpty('')).toBe(true);
      expect(isEmpty('   ')).toBe(true);
    });

    it('应该判断非空字符串为非空', () => {
      expect(isEmpty('hello')).toBe(false);
    });

    it('应该判断空数组为空', () => {
      expect(isEmpty([])).toBe(true);
    });

    it('应该判断非空数组为非空', () => {
      expect(isEmpty([1, 2, 3])).toBe(false);
    });

    it('应该判断空对象为空', () => {
      expect(isEmpty({})).toBe(true);
    });

    it('应该判断非空对象为非空', () => {
      expect(isEmpty({ key: 'value' })).toBe(false);
    });

    it('应该判断数字为非空', () => {
      expect(isEmpty(0)).toBe(false);
      expect(isEmpty(123)).toBe(false);
    });
  });
});

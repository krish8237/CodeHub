export interface TestCase {
  id: string;
  input: string;
  expectedOutput: string;
  isHidden: boolean;
  weight: number;
}

export interface ExecutionResult {
  success: boolean;
  output: string;
  error?: string;
  executionTime: number;
  memoryUsage: number;
  testResults?: TestCaseResult[];
}

export interface TestCaseResult {
  testCaseId: string;
  passed: boolean;
  actualOutput: string;
  expectedOutput: string;
  executionTime: number;
  error?: string;
}

export interface CodingQuestion {
  id: string;
  title: string;
  description: string;
  language: string;
  starterCode: string;
  testCases: TestCase[];
  timeLimit?: number;
  memoryLimit?: number;
}

export interface CodeSubmission {
  questionId: string;
  code: string;
  language: string;
  timestamp: Date;
}

export type SupportedLanguage = 
  | 'python'
  | 'javascript'
  | 'typescript'
  | 'java'
  | 'cpp'
  | 'csharp'
  | 'go'
  | 'rust';

export interface LanguageConfig {
  id: SupportedLanguage;
  name: string;
  monacoLanguage: string;
  defaultCode: string;
  fileExtension: string;
}
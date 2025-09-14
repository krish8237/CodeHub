import axios from 'axios';
import { ExecutionResult, TestCase, SupportedLanguage } from '../types/coding';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ExecuteCodeRequest {
  code: string;
  language: SupportedLanguage;
  input?: string;
}

export interface RunTestsRequest {
  code: string;
  language: SupportedLanguage;
  testCases: TestCase[];
}

class CodeExecutionService {
  private apiClient = axios.create({
    baseURL: `${API_BASE_URL}/api/v1`,
    timeout: 30000, // 30 seconds timeout for code execution
  });

  constructor() {
    // Add request interceptor to include auth token
    this.apiClient.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.apiClient.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access
          localStorage.removeItem('authToken');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Execute code and return the output
   */
  async executeCode(request: ExecuteCodeRequest): Promise<ExecutionResult> {
    try {
      const response = await this.apiClient.post<ExecutionResult>('/execution/run', request);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const errorMessage = error.response?.data?.message || error.message;
        return {
          success: false,
          output: '',
          error: `Execution failed: ${errorMessage}`,
          executionTime: 0,
          memoryUsage: 0,
        };
      }
      throw error;
    }
  }

  /**
   * Run code against test cases
   */
  async runTests(request: RunTestsRequest): Promise<ExecutionResult> {
    try {
      const response = await this.apiClient.post<ExecutionResult>('/execution/test', request);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const errorMessage = error.response?.data?.message || error.message;
        return {
          success: false,
          output: '',
          error: `Test execution failed: ${errorMessage}`,
          executionTime: 0,
          memoryUsage: 0,
        };
      }
      throw error;
    }
  }

  /**
   * Validate code syntax without execution
   */
  async validateSyntax(code: string, language: SupportedLanguage): Promise<{
    valid: boolean;
    errors?: string[];
  }> {
    try {
      const response = await this.apiClient.post('/execution/validate', {
        code,
        language,
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return {
          valid: false,
          errors: [error.response?.data?.message || error.message],
        };
      }
      throw error;
    }
  }

  /**
   * Get supported languages and their configurations
   */
  async getSupportedLanguages(): Promise<{
    languages: Array<{
      id: SupportedLanguage;
      name: string;
      version: string;
      extensions: string[];
    }>;
  }> {
    try {
      const response = await this.apiClient.get('/execution/languages');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch supported languages:', error);
      // Return default languages if API fails
      return {
        languages: [
          { id: 'python', name: 'Python', version: '3.11', extensions: ['.py'] },
          { id: 'javascript', name: 'JavaScript', version: 'Node 18', extensions: ['.js'] },
          { id: 'typescript', name: 'TypeScript', version: '5.0', extensions: ['.ts'] },
          { id: 'java', name: 'Java', version: '17', extensions: ['.java'] },
          { id: 'cpp', name: 'C++', version: 'GCC 11', extensions: ['.cpp', '.cc'] },
          { id: 'csharp', name: 'C#', version: '.NET 7', extensions: ['.cs'] },
          { id: 'go', name: 'Go', version: '1.21', extensions: ['.go'] },
          { id: 'rust', name: 'Rust', version: '1.70', extensions: ['.rs'] },
        ],
      };
    }
  }
}

export const codeExecutionService = new CodeExecutionService();
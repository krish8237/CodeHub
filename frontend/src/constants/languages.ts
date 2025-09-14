import { LanguageConfig } from '../types/coding';

export const SUPPORTED_LANGUAGES: LanguageConfig[] = [
  {
    id: 'python',
    name: 'Python',
    monacoLanguage: 'python',
    fileExtension: 'py',
    defaultCode: `def solution():
    # Write your code here
    pass

# Test your solution
if __name__ == "__main__":
    result = solution()
    print(result)`,
  },
  {
    id: 'javascript',
    name: 'JavaScript',
    monacoLanguage: 'javascript',
    fileExtension: 'js',
    defaultCode: `function solution() {
    // Write your code here
}

// Test your solution
console.log(solution());`,
  },
  {
    id: 'typescript',
    name: 'TypeScript',
    monacoLanguage: 'typescript',
    fileExtension: 'ts',
    defaultCode: `function solution(): any {
    // Write your code here
}

// Test your solution
console.log(solution());`,
  },
  {
    id: 'java',
    name: 'Java',
    monacoLanguage: 'java',
    fileExtension: 'java',
    defaultCode: `public class Solution {
    public static void main(String[] args) {
        Solution sol = new Solution();
        // Test your solution
        System.out.println(sol.solution());
    }
    
    public Object solution() {
        // Write your code here
        return null;
    }
}`,
  },
  {
    id: 'cpp',
    name: 'C++',
    monacoLanguage: 'cpp',
    fileExtension: 'cpp',
    defaultCode: `#include <iostream>
#include <vector>
#include <string>

using namespace std;

class Solution {
public:
    // Write your code here
    void solution() {
        
    }
};

int main() {
    Solution sol;
    sol.solution();
    return 0;
}`,
  },
  {
    id: 'csharp',
    name: 'C#',
    monacoLanguage: 'csharp',
    fileExtension: 'cs',
    defaultCode: `using System;

public class Solution 
{
    public static void Main(string[] args)
    {
        Solution sol = new Solution();
        // Test your solution
        Console.WriteLine(sol.SolutionMethod());
    }
    
    public object SolutionMethod()
    {
        // Write your code here
        return null;
    }
}`,
  },
  {
    id: 'go',
    name: 'Go',
    monacoLanguage: 'go',
    fileExtension: 'go',
    defaultCode: `package main

import "fmt"

func solution() interface{} {
    // Write your code here
    return nil
}

func main() {
    result := solution()
    fmt.Println(result)
}`,
  },
  {
    id: 'rust',
    name: 'Rust',
    monacoLanguage: 'rust',
    fileExtension: 'rs',
    defaultCode: `fn solution() -> Option<i32> {
    // Write your code here
    None
}

fn main() {
    let result = solution();
    println!("{:?}", result);
}`,
  },
];

export const getLanguageConfig = (languageId: string): LanguageConfig | undefined => {
  return SUPPORTED_LANGUAGES.find(lang => lang.id === languageId);
};

export const getDefaultCodeForLanguage = (languageId: string): string => {
  const config = getLanguageConfig(languageId);
  return config?.defaultCode || '';
};
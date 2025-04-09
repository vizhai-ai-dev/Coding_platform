import React, { useState } from 'react';
import { CssBaseline, ThemeProvider, createTheme, Grid, Box, AppBar, Toolbar, Typography, IconButton } from '@mui/material';
import LandingPage from './components/LandingPage';
import CodeEditor from './components/CodeEditor';
import ProblemStatement from './components/ProblemStatement';
import OutputConsole from './components/OutputConsole';
import LightModeIcon from '@mui/icons-material/LightMode';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import SettingsIcon from '@mui/icons-material/Settings';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';

// Sample problems (in a real app, these would come from the backend)
const sampleProblems = {
  arrays: {
    easy: {
      id: "3375",
      title: "Minimum Operations to Make Array Values Equal to K",
      description: `You are given an integer array nums and an integer k.

An integer h is called valid for the current array if all values in the array are strictly greater than h.
      
For example, if nums = [10, 8, 10, 8], a valid h is 7 because all nums[i] > 7. However, 8 is not valid because nums[1] is not strictly greater than 8.

You are allowed to perform the following operation on nums:
- Select an integer h that is valid for the current array.
- For each index i where nums[i] > h, set nums[i] to h.

Return the minimum number of operations required to make every element in nums equal to k. If it is impossible to make all elements equal to k, return -1.`,
      difficulty: "easy",
      examples: [
        {
          input: "nums = [5,2,5,4,5], k = 2",
          output: "2",
          explanation: "The operations can be performed in order using valid integers 4 and then 2."
        },
        {
          input: "nums = [2,1,2], k = 2",
          output: "-1",
          explanation: "It is impossible to make all the values equal to 2."
        }
      ],
      constraints: [
        "2 <= nums.length <= 104",
        "1 <= nums[i] <= 109",
        "1 <= k <= 109"
      ],
      topics: ["Arrays", "Greedy"],
      companies: ["Google", "Amazon"]
    },
    medium: {
      id: "1234",
      title: "Product of Array Except Self",
      description: "Given an integer array nums, return an array answer such that answer[i] is equal to the product of all the elements of nums except nums[i].\nThe product of any prefix or suffix of nums is guaranteed to fit in a 32-bit integer.\nYou must write an algorithm running in O(n) time and without using the division operation.",
      difficulty: "medium",
      examples: [
        {
          input: "nums = [1,2,3,4]",
          output: "[24,12,8,6]",
          explanation: "The products are calculated as:\nanswer[0] = 2*3*4 = 24\nanswer[1] = 1*3*4 = 12\nanswer[2] = 1*2*4 = 8\nanswer[3] = 1*2*3 = 6"
        },
        {
          input: "nums = [-1,1,0,-3,3]",
          output: "[0,0,9,0,0]",
          explanation: "With a zero in the array, most positions will result in zero product."
        }
      ],
      constraints: [
        "2 <= nums.length <= 105",
        "-30 <= nums[i] <= 30",
        "The product of any prefix or suffix of nums is guaranteed to fit in a 32-bit integer."
      ],
      topics: ["Arrays", "Prefix Sum"],
      companies: ["Facebook", "Amazon", "Apple"]
    }
  }
};

function App() {
  const [mode, setMode] = useState<'light' | 'dark'>('dark');
  const [currentView, setCurrentView] = useState<'landing' | 'coding'>('landing');
  const [language, setLanguage] = useState('cpp');
  const [topic, setTopic] = useState('arrays');
  const [difficulty, setDifficulty] = useState('easy');
  const [currentProblem, setCurrentProblem] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const [testResults, setTestResults] = useState<Array<{
    passed: boolean;
    input: string;
    expectedOutput: string;
    actualOutput: string;
    executionTime: number;
    memoryUsage: number;
  }>>([]);

  const [overallMetrics, setOverallMetrics] = useState({
    totalTests: 0,
    passedTests: 0,
    averageTime: 0,
    averageMemory: 0
  });

  // Theme configuration
  const theme = createTheme({
    palette: {
      mode,
      primary: {
        main: mode === 'dark' ? '#90caf9' : '#1976d2',
      },
      background: {
        default: mode === 'dark' ? '#121212' : '#f5f5f5',
        paper: mode === 'dark' ? '#1e1e1e' : '#ffffff',
      },
    },
  });

  // Toggle theme between light and dark
  const toggleTheme = () => {
    setMode(prevMode => prevMode === 'light' ? 'dark' : 'light');
  };

  // Handle start coding button from landing page
  const handleStartCoding = async (selectedLanguage: string, selectedTopic: string, selectedDifficulty: string) => {
    setLanguage(selectedLanguage);
    setTopic(selectedTopic);
    setDifficulty(selectedDifficulty);
    setIsLoading(true);
    
    try {
      // Fetch a problem from the backend API - fixed URL format
      const response = await fetch(`http://localhost:8000/api/problems/generate?topic=${selectedTopic}&difficulty=${selectedDifficulty}`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      
      const problem = await response.json();
      setCurrentProblem(problem);
      setCurrentView('coding');
    } catch (error) {
      console.error('Error fetching problem:', error);
      // Fallback to sample problems if backend fails
      const problem = sampleProblems[selectedTopic as keyof typeof sampleProblems]?.[selectedDifficulty as keyof typeof sampleProblems.arrays];
      
      if (problem) {
        setCurrentProblem(problem);
        setCurrentView('coding');
      } else {
        alert('No problem found with the selected criteria. Using default problem.');
        setCurrentProblem(sampleProblems.arrays.easy);
        setCurrentView('coding');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunCode = async (code: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/code/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code,
          language,
          problem_id: currentProblem?.id || '1'
        }),
      });
      
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      
      const data = await response.json();
      
      // Use the test results directly from the backend
      if (data.test_results && data.test_results.length > 0) {
        setTestResults(data.test_results);
        setOverallMetrics(data.overall_metrics || {
          totalTests: data.test_results.length,
          passedTests: data.test_results.filter((r: any) => r.passed).length,
          averageTime: data.test_results.reduce((sum: number, r: any) => sum + r.execution_time, 0) / data.test_results.length,
          averageMemory: data.test_results.reduce((sum: number, r: any) => sum + r.memory_usage, 0) / data.test_results.length
        });
      } else {
        // Fallback for backward compatibility
        if (currentProblem?.examples[0]) {
          setTestResults([{
            passed: Math.random() > 0.5, // Random pass/fail for demo
            input: currentProblem.examples[0].input,
            expectedOutput: currentProblem.examples[0].output,
            actualOutput: data.output || currentProblem.examples[0].output,
            executionTime: data.execution_time || Math.floor(Math.random() * 100),
            memoryUsage: data.memory_usage || Math.floor(Math.random() * 5000)
          }]);
        }
      }
    } catch (error) {
      console.error('Error running code:', error);
      // Create mock test result for demonstration
      if (currentProblem?.examples[0]) {
        setTestResults([{
          passed: false,
          input: currentProblem.examples[0].input,
          expectedOutput: currentProblem.examples[0].output,
          actualOutput: "Error executing code",
          executionTime: 0,
          memoryUsage: 0
        }]);
      }
    }
  };

  const handleSubmitCode = async (code: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/code/evaluate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code,
          language,
          problem_id: currentProblem?.id || '1'
        }),
      });
      
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      
      const data = await response.json();
      setTestResults(data.test_results || []);
      setOverallMetrics(data.overall_metrics || {
        totalTests: 0,
        passedTests: 0,
        averageTime: 0,
        averageMemory: 0
      });
    } catch (error) {
      console.error('Error submitting code:', error);
      // Mock data for demonstration
      if (currentProblem?.examples) {
        const mockResults = currentProblem.examples.map((example: any, index: number) => ({
          passed: Math.random() > 0.3, // Random pass/fail with bias toward passing
          input: example.input,
          expectedOutput: example.output,
          actualOutput: index === 0 ? example.output : "Different output",
          executionTime: Math.floor(Math.random() * 100),
          memoryUsage: Math.floor(Math.random() * 5000)
        }));
        
        setTestResults(mockResults);
        
        const passedCount = mockResults.filter((r: any) => r.passed).length;
        setOverallMetrics({
          totalTests: mockResults.length,
          passedTests: passedCount,
          averageTime: mockResults.reduce((sum: number, r: any) => sum + r.executionTime, 0) / mockResults.length,
          averageMemory: mockResults.reduce((sum: number, r: any) => sum + r.memoryUsage, 0) / mockResults.length
        });
      }
    }
  };

  const handleLanguageChange = (newLanguage: string) => {
    setLanguage(newLanguage);
  };

  // Render the appropriate view
  const renderContent = () => {
    if (currentView === 'landing') {
      return <LandingPage onStart={handleStartCoding} isLoading={isLoading} />;
    }
    
    return (
      <Grid container spacing={2} sx={{ height: 'calc(100vh - 64px)' }}>
        {/* @ts-ignore */}
        <Grid item xs={12} md={5} lg={4}>
          {currentProblem && (
            <ProblemStatement 
              problemId={currentProblem.id}
              title={currentProblem.title}
              description={currentProblem.description}
              difficulty={currentProblem.difficulty}
              examples={currentProblem.examples}
              constraints={currentProblem.constraints}
              topics={currentProblem.topics}
              companies={currentProblem.companies}
            />
          )}
        </Grid>
        {/* @ts-ignore */}
        <Grid item xs={12} md={7} lg={8}>
          <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <Box sx={{ flexGrow: 1, mb: 2 }}>
              <CodeEditor
                initialCode=""
                language={language}
                onRunCode={handleRunCode}
                onSubmitCode={handleSubmitCode}
                onLanguageChange={handleLanguageChange}
              />
            </Box>
            <Box sx={{ height: '40%' }}>
              <OutputConsole
                testResults={testResults}
                overallMetrics={overallMetrics}
              />
            </Box>
          </Box>
        </Grid>
      </Grid>
    );
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <AppBar position="static" color="default" elevation={1}>
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Coding Platform
            </Typography>
            <IconButton onClick={toggleTheme} color="inherit">
              {mode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>
            <IconButton color="inherit">
              <SettingsIcon />
            </IconButton>
            <IconButton color="inherit">
              <AccountCircleIcon />
            </IconButton>
          </Toolbar>
        </AppBar>
        <Box component="main" sx={{ flexGrow: 1, p: 2 }}>
          {renderContent()}
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;

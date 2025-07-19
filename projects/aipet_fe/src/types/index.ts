import React from 'react';

// Global type definitions
export interface AppConfig {
  apiUrl: string;
  environment: 'development' | 'production' | 'test';
}

// Rive animation types
export interface RiveAnimationConfig {
  src: string;
  stateMachines: string;
  autoplay?: boolean;
  layout?: any;
}

// Component prop types
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

// API response types
export interface ApiResponse<T = any> {
  data: T;
  status: number;
  message?: string;
}

// Error types
export interface AppError {
  message: string;
  code?: string;
  details?: any;
} 
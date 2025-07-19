# AI Pet Frontend

A React TypeScript application for the AI Pet project featuring Rive animations.

## Features

- React 18 with TypeScript
- Rive animations integration
- Modern development setup with ESLint and Prettier
- Path aliases for clean imports
- Type-safe development

## Prerequisites

- Node.js 16+ 
- npm or yarn

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
# or
npm start
```

## Available Scripts

- `npm start` - Start development server
- `npm run dev` - Alias for start
- `npm run build` - Build for production
- `npm run test` - Run tests
- `npm run lint` - Lint and fix code
- `npm run type-check` - Run TypeScript type checking
- `npm run clean` - Clean build artifacts

## Project Structure

```
src/
├── components/     # React components
├── types/         # TypeScript type definitions
├── utils/         # Utility functions
├── styles/        # CSS and styling
├── App.tsx        # Main app component
└── index.tsx      # App entry point
```

## TypeScript Configuration

The project uses a modern TypeScript configuration with:
- Strict type checking
- Path aliases for clean imports
- React JSX support
- Modern ES6+ features

## Path Aliases

You can use the following path aliases for clean imports:

- `@/*` - Points to `src/*`
- `@/components/*` - Points to `src/components/*`
- `@/types/*` - Points to `src/types/*`
- `@/utils/*` - Points to `src/utils/*`
- `@/styles/*` - Points to `src/styles/*`

Example:
```typescript
import { BaseComponentProps } from '@/types';
import { MyComponent } from '@/components/MyComponent';
``` 
import { useState, useCallback } from 'react';
import { apiClient, ApiResponse, PetNeedsRequest, PetActionRecommendation } from '../api/client';

export interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export const useApi = <T>() => {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(async (apiCall: () => Promise<ApiResponse<T>>) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const response = await apiCall();
      
      if (response.error) {
        setState(prev => ({ 
          ...prev, 
          loading: false, 
          error: response.error || 'An error occurred' 
        }));
        return response;
      }
      
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        data: response.data || null 
      }));
      
      return response;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unexpected error occurred';
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: errorMessage 
      }));
      throw error;
    }
  }, []);

  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
    });
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
};

// Specialized hook for pet recommendations
export const usePetRecommendations = () => {
  const [recommendations, setRecommendations] = useState<PetActionRecommendation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getRecommendations = useCallback(async (petNeeds: PetNeedsRequest, model?: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.getPetRecommendations(petNeeds, model);
      
      if (response.error) {
        setError(response.error);
        return null;
      }
      
      if (response.data) {
        setRecommendations(response.data);
        return response.data;
      }
      
      return null;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get recommendations';
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setRecommendations(null);
    setLoading(false);
    setError(null);
  }, []);

  return {
    recommendations,
    loading,
    error,
    getRecommendations,
    reset,
  };
};

// Hook for authentication status
export const useAuthStatus = () => {
  const isAuthenticated = apiClient.isAuthenticated();
  const token = apiClient.getToken();
  
  return {
    isAuthenticated,
    token,
  };
}; 
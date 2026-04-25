import { useState } from 'react';
import { useForm as useHookForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Send, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';

const querySchema = z.object({
  query: z.string().min(5, "Query must be at least 5 characters").max(1000, "Maximum 1000 characters"),
});

type QueryFormData = z.infer<typeof querySchema>;

interface QueryFormProps {
  onSubmit: (query: string) => Promise<void>;
  isLoading: boolean;
}

export function QueryForm({ onSubmit, isLoading }: QueryFormProps) {
  const { register, handleSubmit, formState: { errors }, watch } = useHookForm<QueryFormData>({
    resolver: zodResolver(querySchema),
    defaultValues: { query: '' }
  });

  const queryValue = watch('query');
  const count = queryValue?.length || 0;

  const handleFormSubmit = async (data: QueryFormData) => {
    await onSubmit(data.query);
  };

  return (
    <Card className="border-brand-cyan/20 glass-panel shadow-brand-cyan/5 shadow-lg">
      <CardHeader>
        <CardTitle className="text-xl flex items-center">
          <Send className="mr-2 h-5 w-5 text-brand-cyan" />
          Ask the Agents
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
          <div className="relative">
            <Input
              {...register('query')}
              placeholder="e.g. What are the latest AI trends in 2026?"
              disabled={isLoading}
              className="pr-20 h-12 text-base transition-all focus:border-brand-violet focus:ring-brand-violet/20"
            />
            <div className="absolute right-3 top-3 text-xs text-muted-foreground">
              {count}/1000
            </div>
          </div>
          {errors.query && <p className="text-sm text-destructive">{errors.query.message}</p>}
          
          <Button 
            type="submit" 
            disabled={isLoading || count === 0} 
            className="w-full h-12 bg-gradient-to-r from-brand-violet to-brand-cyan hover:opacity-90 text-white font-medium shadow-md shadow-brand-violet/20 transition-all"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Agents working...
              </>
            ) : (
              'Submit Query'
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

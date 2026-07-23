export type Idea = {
  id: number;
  title: string;
  description: string;
  team_size: number;
  tags: string[];
  created_at: string;
};

export type IdeaInput = {
  title: string;
  description: string;
  team_size: number;
  tags: string[];
};

export type IdeaAnalysis = {
  idea_id: number;
  analysis: string;
  model: string;
  prompt_tokens: number;
  completion_tokens: number;
  created_at: string;
};

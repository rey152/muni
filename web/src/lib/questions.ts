// The three "What I want to know" questions. Each one picks matters by what their
// reviewed records show, never by guessing.
import { data } from './data';
import type { Matter } from './data';
import { hasDecisionRecord, missingStages } from './civic';

export interface Question {
  key: string;
  title: string;
  explanation: string;
  matches: (matter: Matter) => boolean;
}

export const QUESTIONS: Question[] = [
  {
    key: 'decided',
    title: "What's been decided?",
    explanation: 'Matters with a decision, a by-law in force, or a repeal in the records checked.',
    matches: hasDecisionRecord,
  },
  {
    key: 'have-a-say',
    title: 'Can I still have a say?',
    explanation: 'Every matter, with each way to have a say that the records state. Open or closed comes only from a quoted date.',
    matches: () => true,
  },
  {
    key: 'undecided',
    title: "What's still undecided?",
    explanation: 'Matters with points marked not decided, or with no decision or in-force record found yet.',
    matches: (matter) => matter.claims.some((c) => c.section === 'not_decided') || missingStages(matter).length > 0,
  },
];

export function questionMatters(question: Question): Matter[] {
  return data.matters.filter(question.matches);
}

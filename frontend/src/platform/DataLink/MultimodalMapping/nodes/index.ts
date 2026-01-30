export { default as SourceNode } from './SourceNode';
export { default as TransformNode } from './TransformNode';
export { default as TargetNode } from './TargetNode';

import SourceNode from './SourceNode';
import TransformNode from './TransformNode';
import TargetNode from './TargetNode';

export const nodeTypes = {
  source: SourceNode,
  transform: TransformNode,
  target: TargetNode,
};

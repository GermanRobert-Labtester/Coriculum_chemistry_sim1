/* Ambient declarations for the N21 runtime modules.
 *
 * The simulator ships as a single offline file with no package manager and no
 * node_modules tree, so the runtime modules cannot depend on @types/node.
 * These declarations describe exactly the host surface the modules use: the
 * CommonJS export guard used by the Node harnesses and the V8 stack helper.
 */

declare const module: { exports: unknown } | undefined;

interface ErrorConstructor {
  captureStackTrace?: (target: object, constructor?: Function) => void;
}

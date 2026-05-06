import { neon, NeonQueryFunction } from '@neondatabase/serverless';

// Lazy singleton — neon() is NOT called at module load time so build succeeds without DATABASE_URL
let _sql: NeonQueryFunction<false, false> | null = null;

function getInstance(): NeonQueryFunction<false, false> {
  if (!_sql) {
    _sql = neon(process.env.DATABASE_URL!);
  }
  return _sql;
}

// Proxy forwards template-literal calls and property access to the lazy instance
const sql = new Proxy(
  function () {} as unknown as NeonQueryFunction<false, false>,
  {
    apply(_target, thisArg, args) {
      return Reflect.apply(
        getInstance() as unknown as (...a: unknown[]) => unknown,
        thisArg,
        args
      );
    },
    get(_target, prop) {
      return (getInstance() as unknown as Record<string | symbol, unknown>)[prop];
    },
  }
);

export { sql };
export default sql;

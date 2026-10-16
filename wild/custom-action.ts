import { resolveSafeChildPath } from '@backstage/backend-plugin-api';
import { createTemplateAction } from '@backstage/plugin-scaffolder-node';
import fs from 'fs-extra';

// Create a custom Backstage Scaffolder action
export const createMyCustomAction = () =>
  createTemplateAction({
    id: 'my:custom:action',
    description: 'Creates a new file in the temporary workspace',

    // Define the inputs required by the action
    schema: {
      input: {
        filename: z => z.string().min(1),
        contents: z => z.string(),
      },
    },

    // Execute the action
    async handler(ctx) {
      // Get a safe file path inside the temporary workspace
      const filePath = resolveSafeChildPath(
        ctx.workspacePath,
        ctx.input.filename,
      );

      // Create the file and write its contents
      await fs.outputFile(filePath, ctx.input.contents);

      ctx.logger.info(`Created file: ${ctx.input.filename}`);
    },
  });

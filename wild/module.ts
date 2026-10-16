import { createBackendModule } from '@backstage/backend-plugin-api';
import { scaffolderActionsExtensionPoint } from '@backstage/plugin-scaffolder-node/alpha';
import { createMyCustomAction } from './action';

// Register the custom action with the Scaffolder plugin
export default createBackendModule({
  pluginId: 'scaffolder',
  moduleId: 'my-custom-action',

  register(reg) {
    reg.registerInit({
      deps: {
        scaffolder: scaffolderActionsExtensionPoint,
      },

      async init({ scaffolder }) {
        scaffolder.addActions(createMyCustomAction());
      },
    });
  },
});

import { openIconModal } from "./modal.js";
import { isValidIconName, isValidSize, DEFAULT_SIZE } from "./icons.js";

const ZWSP = "\u200B";

export class IconSource extends window.React.Component {
  componentDidMount() {
    const { editorState, entityType, onComplete, onClose } = this.props;
    openIconModal().then((choice) => {
      if (!choice || !isValidIconName(choice.name)) {
        onClose();
        return;
      }
      const size = isValidSize(choice.size) ? choice.size : DEFAULT_SIZE;
      const { Modifier, EditorState } = window.DraftJS;
      const content = editorState.getCurrentContent();
      const rawSelection = editorState.getSelection();
      const selection = rawSelection.isCollapsed()
        ? rawSelection
        : rawSelection.merge({
            anchorKey: rawSelection.getFocusKey(),
            anchorOffset: rawSelection.getFocusOffset(),
          });
      const contentWithEntity = content.createEntity(entityType.type, "IMMUTABLE", {
        name: choice.name,
        size,
      });
      const entityKey = contentWithEntity.getLastCreatedEntityKey();
      const newContent = Modifier.replaceText(
        contentWithEntity,
        selection,
        ZWSP,
        null,
        entityKey,
      );
      const nextState = EditorState.push(editorState, newContent, "insert-characters");
      onComplete(nextState);
    });
  }

  render() {
    return null;
  }
}
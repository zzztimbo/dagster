import * as React from "react";
import gql from "graphql-tag";
import styled from "styled-components/macro";
import { Colors, Icon } from "@blueprintjs/core";
import PythonErrorInfo from "../PythonErrorInfo";
import { showCustomAlert } from "../CustomAlertProvider";
import {
  ValidationResult,
  ValidationError
} from "../configeditor/codemirror-yaml/mode";
import {
  ConfigEditorEnvironmentSchemaFragment,
  ConfigEditorEnvironmentSchemaFragment_allConfigTypes_CompositeConfigType
} from "../configeditor/types/ConfigEditorEnvironmentSchemaFragment";
import { RunPreviewExecutionPlanResultFragment } from "./types/RunPreviewExecutionPlanResultFragment";

interface IRunPreviewProps {
  plan: RunPreviewExecutionPlanResultFragment | null;
  validationResult: ValidationResult | null;

  toolbarActions?: React.ReactChild;
  environmentSchema: ConfigEditorEnvironmentSchemaFragment;
  onHighlightValidationError: (error: ValidationError) => void;
}

export class RunPreview extends React.Component<IRunPreviewProps> {
  static fragments = {
    RunPreviewExecutionPlanResultFragment: gql`
      fragment RunPreviewExecutionPlanResultFragment on ExecutionPlanResult {
        __typename
        ... on ExecutionPlan {
          __typename
        }
        ... on PipelineNotFoundError {
          message
        }
        ... on InvalidSubsetError {
          message
        }
        ...PythonErrorFragment
      }
      ${PythonErrorInfo.fragments.PythonErrorFragment}
    `
  };

  shouldComponentUpdate(nextProps: IRunPreviewProps) {
    return (
      nextProps.validationResult !== this.props.validationResult ||
      nextProps.plan !== this.props.plan
    );
  }

  getRootCompositeChildren = () => {
    const {
      allConfigTypes,
      rootEnvironmentType
    } = this.props.environmentSchema;
    const children: {
      [fieldName: string]: ConfigEditorEnvironmentSchemaFragment_allConfigTypes_CompositeConfigType;
    } = {};

    const root = allConfigTypes.find(t => t.key === rootEnvironmentType.key);
    if (root?.__typename !== "CompositeConfigType") return children;

    root.fields.forEach(field => {
      const allConfigVersion = allConfigTypes.find(
        t => t.key === field.configTypeKey
      );
      if (allConfigVersion?.__typename !== "CompositeConfigType") return;
      children[field.name] = allConfigVersion;
    });

    return children;
  };

  render() {
    const {
      validationResult,
      plan,
      toolbarActions,
      onHighlightValidationError
    } = this.props;

    const errors: (ValidationError | React.ReactNode)[] = [];
    const errorsByNode: { [path: string]: ValidationError[] } = {};

    if (validationResult && !validationResult.isValid) {
      validationResult.errors.forEach(e => {
        errors.push(e);

        const path: string[] = [];
        for (const component of e.path) {
          path.push(component);
          const key = path.join(".");
          errorsByNode[key] = errorsByNode[key] || [];
          errorsByNode[key].push(e);
        }
      });
    }

    if (plan?.__typename === "InvalidSubsetError") {
      errors.push(plan.message);
    }

    if (plan?.__typename === "PythonError") {
      const info = <PythonErrorInfo error={plan} />;
      errors.push(
        <>
          PythonError{" "}
          <span onClick={() => showCustomAlert({ body: info })}>
            click for details
          </span>
        </>
      );
    }

    const { resources, solids, ...rest } = this.getRootCompositeChildren();

    const itemsIn = (parents: string[], names: string[]) =>
      names.map(name => {
        const path = [...parents, name];
        const errors = errorsByNode[path.join(".")];
        const present = pathExistsInObject(path, validationResult?.document);
        return (
          <Item
            key={name}
            isPresent={present}
            isInvalid={!!errors}
            onClick={() =>
              onHighlightValidationError(
                errors ? errors[0] : { path, message: "", reason: "" }
              )
            }
          >
            {name}
          </Item>
        );
      });

    return (
      <div style={{ display: "flex", alignItems: "stretch", height: "100%" }}>
        <ErrorsList>
          <Section>
            <SectionTitle>Errors</SectionTitle>
            {errors.map((e, idx) => (
              <ErrorRow
                key={idx}
                error={e}
                onClick={onHighlightValidationError}
              />
            ))}
          </Section>
        </ErrorsList>
        <div style={{ overflow: "scroll", minWidth: "30%", maxWidth: "60%" }}>
          <RuntimeAndResourcesSection>
            <Section>
              <SectionTitle>Runtime</SectionTitle>
              <ItemSet>{itemsIn([], Object.keys(rest))}</ItemSet>
            </Section>
            {(resources?.fields.length || 0) > 0 && (
              <Section>
                <SectionTitle>Resources</SectionTitle>
                <ItemSet>
                  {itemsIn(
                    ["resources"],
                    (resources?.fields || []).map(f => f.name)
                  )}
                </ItemSet>
              </Section>
            )}
          </RuntimeAndResourcesSection>
          <Section>
            <SectionTitle>Solids</SectionTitle>
            <ItemSet>
              {itemsIn(
                ["solids"],
                (solids?.fields || []).map(f => f.name)
              )}
            </ItemSet>
          </Section>
          <div style={{ height: 50 }} />
        </div>
        <div style={{ position: "fixed", bottom: 14, right: 14 }}>
          {toolbarActions}
        </div>
      </div>
    );
  }
}

const SectionTitle = styled.div`
  color: ${Colors.GRAY3};
  text-transform: uppercase;
  font-size: 12px;
`;
const Section = styled.div`
  margin-top: 14px;
  margin-left: 10px;
`;

const ItemSet = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
`;

const Item = styled.div<{ isInvalid: boolean; isPresent: boolean }>`
  white-space: nowrap;
  font-size: 13px;
  color: ${({ isInvalid }) => (isInvalid ? Colors.WHITE : Colors.BLACK)};
  background: ${({ isInvalid, isPresent }) =>
    isInvalid ? Colors.RED5 : isPresent ? Colors.LIGHT_GRAY2 : Colors.WHITE};
  border-radius: 3px;
  border: 1px dashed
    ${({ isPresent }) => (isPresent ? "transparent" : Colors.GRAY5)};
  padding: 3px 5px;
  margin: 3px;
  transition: background 150ms linear, color 150ms linear;
  cursor: default;

  &:hover {
    transition: none;
    background: ${({ isInvalid, isPresent }) =>
      isInvalid ? Colors.RED3 : isPresent ? Colors.GRAY5 : Colors.WHITE};
  }
`;

const ErrorsList = styled.div`
  margin-left: 10px;
  min-width: 50%;
  border-right: 1px solid #ccc;
  overflow: scroll;
`;

const ErrorRowContainer = styled.div<{ hoverable: boolean }>`
  text-align: left;
  font-size: 13px;
  white-space: pre-wrap;
  word-break: break-word;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  border-bottom: 1px solid #ccc;
  padding: 7px 0;
  padding-right: 7px;
  margin-bottom: 8px;
  &:last-child {
    border-bottom: 0;
    margin-bottom: 15px;
  }
  ${({ hoverable }) =>
    hoverable &&
    `&:hover {
      background: ${Colors.LIGHT_GRAY5};
    }
  `}
`;

const RuntimeAndResourcesSection = styled.div`
  display: flex;
  @media (max-width: 800px) {
    flex-direction: column;
  }
`;

const ErrorRow: React.FunctionComponent<{
  error: ValidationError | React.ReactNode;
  onClick: (error: ValidationError) => void;
}> = ({ error, onClick }) => {
  let message = error;
  let target: ValidationError | null = null;
  if (error && typeof error === "object" && "message" in error) {
    message = error.message;
    target = error;
  }

  let displayed = message;
  if (typeof message === "string" && message.length > 400) {
    displayed = truncateErrorMessage(message);
  }

  return (
    <ErrorRowContainer
      hoverable={!!target}
      onClick={() => target && onClick(target)}
    >
      <div style={{ paddingRight: 8 }}>
        <Icon icon="error" iconSize={14} color={Colors.RED4} />
      </div>
      <div>
        {displayed}
        {displayed !== message && (
          <a
            onClick={() =>
              showCustomAlert({
                body: <div style={{ whiteSpace: "pre-wrap" }}>{message}</div>
              })
            }
          >
            View&nbsp;All&nbsp;&gt;
          </a>
        )}
      </div>
    </ErrorRowContainer>
  );
};

function truncateErrorMessage(message: string) {
  let split = message.indexOf("{");
  if (split === -1) {
    split = message.indexOf(". ");
  }
  if (split === -1) {
    split = 400;
  }
  return message.substr(0, split) + "... ";
}

function pathExistsInObject(path: string[], object: any): boolean {
  if (!object || typeof object !== "object") return false;
  if (path.length === 0) return true;
  const [first, ...rest] = path;
  return pathExistsInObject(rest, object[first]);
}

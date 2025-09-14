import { isRouteErrorResponse, useRouteError } from "react-router";

export default function MyErrorPage() {
  const error = useRouteError();

  if (isRouteErrorResponse(error)) {
    return <h1>Error {error.status}: {error.statusText}</h1>;
  }

  return <h1>Unexpected error: {(error as Error).message}</h1>;
}



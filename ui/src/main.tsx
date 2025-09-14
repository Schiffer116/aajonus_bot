import { createRoot } from 'react-dom/client'
import './index.css'
import { createBrowserRouter } from "react-router";
import { RouterProvider } from "react-router/dom";
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import Home from './pages/Home';
import Browse, { browseLoader } from './pages/Home/Browse';
import DocumentViewer, { documentLoader } from './pages/Home/DocumentViewer';
import Chat from './pages/Home/Chat';
import Error from './pages/Error';

const queryClient = new QueryClient()

const router = createBrowserRouter([
  {
    element: <Home />,
    errorElement: <Error />,
    children: [
      {
        path: "browse",
        loader: browseLoader(queryClient),
        element: <Browse />
      },
      {
        path: "document/:id?",
        loader: documentLoader,
        element: <DocumentViewer />
      },
      {
        path: "chat",
        element: <Chat />
      }
    ]
  },
]);

createRoot(document.getElementById('root')!).render(
  <QueryClientProvider client={queryClient}>
    <RouterProvider router={router} />
  </QueryClientProvider>
)

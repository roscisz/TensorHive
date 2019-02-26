import DashView from './components/TheDash.vue'
import LoginView from './components/TheLogin.vue'
import NotFoundView from './components/404.vue'
// Import Views - Dash
import CalendarView from './components/views/ReservationsOverview.vue'
import WatchView from './components/views/NodesOverview.vue'
import UsersView from './components/views/UsersOverview.vue'
// Routes
const routes = [
  {
    path: '/',
    component: DashView,
    children: [
      {
        path: '/reservations_overview',
        alias: '',
        component: CalendarView,
        name: 'Reservation Overview',
        meta: {
          description: 'Calendar with reservations',
          requiresAuth: true,
          role: 'user'
        }
      },
      {
        path: 'nodes_overview',
        alias: '',
        component: WatchView,
        name: 'Nodes overview',
        meta: {
          description: 'Informations about nodes',
          requiresAuth: true,
          role: 'user'
        }
      },
      {
        path: 'users_overview',
        alias: '',
        component: UsersView,
        name: 'Users overview',
        meta: {
          description: 'Table users view for admin',
          requiresAuth: true,
          role: 'admin'
        }
      }
    ]
  },
  {
    path: '/login',
    component: LoginView,
    meta: {
      role: 'user'
    }
  },
  {
    path: '*',
    component: NotFoundView
  }
]

export default routes

import DashView from './components/TheDash.vue'
import LoginView from './components/TheLogin.vue'
import RegisterView from './components/TheRegister.vue'
import NotFoundView from './components/404.vue'
// Import Views - Dash
import CalendarView from './components/views/ReservationsOverview.vue'
import WatchView from './components/views/NodesOverview.vue'
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
    path: '/register',
    component: RegisterView,
    meta: {
      requiresAuth: true,
      role: 'admin'
    }
  },
  {
    path: '*',
    component: NotFoundView
  }
]

export default routes

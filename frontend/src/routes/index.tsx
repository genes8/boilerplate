import { createFileRoute, Link, Navigate } from '@tanstack/react-router'
import { useAuth } from '@/hooks/useAuth'
import { Button } from '@/components/ui/button'
import { motion } from 'motion/react'
import { 
  Shield, 
  LayoutDashboard, 
  ArrowRight,
  Lock,
  Code,
  ChevronRight
} from 'lucide-react'

export const Route = createFileRoute('/')({ component: LandingPage })

function LandingPage() {
  const { isAuthenticated } = useAuth()

  if (isAuthenticated) {
    return <Navigate to="/dashboard" />
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.2,
      },
    },
  }

  const itemVariants = {
    hidden: { 
      opacity: 0, 
      y: 30,
      rotateX: -10,
    },
    visible: {
      opacity: 1,
      y: 0,
      rotateX: 0,
      transition: {
        type: 'spring' as const,
        stiffness: 100,
        damping: 15,
      },
    },
  }

  const featureVariants = {
    hidden: { 
      opacity: 0, 
      y: 50,
      scale: 0.95,
    },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        type: 'spring' as const,
        stiffness: 80,
        damping: 12,
      },
    },
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 overflow-hidden">
      {/* Animated background grid */}
      <div className="fixed inset-0 pointer-events-none">
        <motion.div
          className="absolute inset-0 opacity-5"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)
            `,
            backgroundSize: '60px 60px',
          }}
          animate={{
            backgroundPosition: ['0 0', '60px 60px'],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: 'linear',
          }}
        />
      </div>

      <div className="relative z-10">
        {/* Hero Section */}
        <section className="min-h-screen flex items-center justify-center px-6 py-20">
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="max-w-6xl mx-auto"
          >
            {/* Badge */}
            <motion.div variants={itemVariants} className="mb-8">
              <motion.div
                className="inline-flex items-center gap-2 px-4 py-2 border border-neutral-800 bg-neutral-900/50 backdrop-blur-sm rounded-full"
                whileHover={{
                  borderColor: 'rgba(255,255,255,0.3)',
                  scale: 1.02,
                }}
                transition={{ type: 'spring', stiffness: 400, damping: 17 }}
              >
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                <span className="text-sm text-neutral-400 font-medium tracking-wide">
                  PRODUCTION-READY
                </span>
              </motion.div>
            </motion.div>

            {/* Main Heading */}
            <motion.div variants={itemVariants} className="mb-8">
              <h1 className="text-7xl md:text-9xl font-bold tracking-tight leading-none mb-4">
                <span className="block text-neutral-500">Enterprise</span>
                <span className="block text-neutral-50">Boilerplate</span>
              </h1>
            </motion.div>

            {/* Subheading */}
            <motion.p
              variants={itemVariants}
              className="text-xl md:text-2xl text-neutral-400 max-w-2xl mb-12 leading-relaxed font-light"
            >
              Ship faster with a battle-tested foundation. Authentication, RBAC, and
              modern UI—ready day one.
            </motion.p>

            {/* CTA Buttons */}
            <motion.div variants={itemVariants} className="flex flex-col sm:flex-row gap-4">
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Link to="/auth/login" params={{}}>
                  <Button
                    size="lg"
                    className="bg-neutral-50 text-neutral-950 hover:bg-neutral-100 border-0 px-8 py-6 text-lg font-medium h-auto"
                  >
                    Get Started
                    <ArrowRight className="w-5 h-5 ml-2" />
                  </Button>
                </Link>
              </motion.div>
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Link to="/auth/register" params={{}}>
                  <Button
                    size="lg"
                    variant="outline"
                    className="bg-neutral-900 border-neutral-600 text-neutral-50 hover:bg-neutral-800 hover:border-neutral-500 px-8 py-6 text-lg font-medium h-auto"
                  >
                    Create Account
                  </Button>
                </Link>
              </motion.div>
            </motion.div>

            {/* Stats */}
            <motion.div
              variants={itemVariants}
              className="grid grid-cols-3 gap-8 mt-20 pt-20 border-t border-neutral-800"
            >
              {[
                { label: 'Production', value: 'Ready' },
                { label: 'Type', value: 'Safe' },
                { label: 'Open', value: 'Source' },
              ].map((stat, index) => (
                <motion.div
                  key={index}
                  className="text-center"
                  whileHover={{ y: -5 }}
                  transition={{ type: 'spring', stiffness: 300, damping: 15 }}
                >
                  <div className="text-3xl md:text-4xl font-bold text-neutral-50 mb-2">
                    {stat.value}
                  </div>
                  <div className="text-sm text-neutral-500 uppercase tracking-widest">
                    {stat.label}
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </motion.div>
        </section>

        {/* Features Section */}
        <section className="py-32 px-6">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-100px' }}
              transition={{ duration: 0.6 }}
              className="mb-20"
            >
              <h2 className="text-5xl md:text-6xl font-bold tracking-tight mb-6">
                Built for <span className="text-neutral-500">scale</span>
              </h2>
              <p className="text-xl text-neutral-400 max-w-2xl">
                Everything you need to build enterprise applications, nothing you don't.
              </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                {
                  icon: Lock,
                  title: 'Authentication',
                  description: 'JWT-based auth with HTTP-only cookies, OIDC/SSO support, and secure password reset flow.',
                  color: 'from-blue-500 to-cyan-500',
                },
                {
                  icon: Shield,
                  title: 'RBAC System',
                  description: 'Role-Based Access Control with granular permissions, scope hierarchy, and admin UI.',
                  color: 'from-violet-500 to-purple-500',
                },
                {
                  icon: LayoutDashboard,
                  title: 'Modern UI',
                  description: 'Beautiful components with shadcn/ui, Tailwind CSS, and responsive design.',
                  color: 'from-emerald-500 to-teal-500',
                },
              ].map((feature, index) => (
                <motion.div
                  key={index}
                  variants={featureVariants}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true, margin: '-50px' }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ y: -8, scale: 1.02 }}
                  className="group"
                >
                  <div className="relative h-full p-8 border border-neutral-800 bg-neutral-900/30 backdrop-blur-sm overflow-hidden">
                    {/* Hover gradient effect */}
                    <motion.div
                      className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-5 transition-opacity duration-500`}
                    />
                    
                    {/* Icon */}
                    <motion.div
                      className={`relative w-16 h-16 rounded-2xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-6`}
                      whileHover={{ rotate: 5, scale: 1.1 }}
                      transition={{ type: 'spring', stiffness: 300, damping: 15 }}
                    >
                      <feature.icon className="w-8 h-8 text-white" />
                    </motion.div>

                    {/* Content */}
                    <div className="relative">
                      <h3 className="text-2xl font-bold mb-3 group-hover:text-neutral-200 transition-colors">
                        {feature.title}
                      </h3>
                      <p className="text-neutral-400 leading-relaxed">
                        {feature.description}
                      </p>
                    </div>

                    {/* Arrow indicator */}
                    <motion.div
                      className="relative mt-6 flex items-center gap-2 text-sm text-neutral-500 group-hover:text-neutral-300 transition-colors"
                      initial={{ opacity: 0 }}
                      whileHover={{ opacity: 1 }}
                    >
                      Learn more
                      <ChevronRight className="w-4 h-4" />
                    </motion.div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Tech Stack Section */}
        <section className="py-32 px-6 border-t border-neutral-800">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.6 }}
            className="max-w-4xl mx-auto"
          >
            <div className="border border-neutral-800 bg-neutral-900/50 backdrop-blur-sm p-12">
              <div className="flex items-start gap-6 mb-8">
                <motion.div
                  className="w-12 h-12 rounded-xl bg-neutral-800 flex items-center justify-center flex-shrink-0"
                  whileHover={{ rotate: 180, scale: 1.1 }}
                  transition={{ type: 'spring', stiffness: 200, damping: 10 }}
                >
                  <Code className="w-6 h-6 text-neutral-400" />
                </motion.div>
                <div>
                  <h3 className="text-3xl font-bold mb-4">Tech Stack</h3>
                  <p className="text-neutral-400">
                    Modern, battle-tested technologies chosen for performance and developer experience.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                {[
                  { label: 'Backend', value: 'FastAPI + PostgreSQL' },
                  { label: 'Frontend', value: 'TanStack Start + React' },
                  { label: 'Cache', value: 'Redis 7' },
                  { label: 'Deploy', value: 'Docker + Hetzner' },
                ].map((item, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.1 }}
                    whileHover={{ x: 5 }}
                  >
                    <div className="text-sm text-neutral-500 uppercase tracking-widest mb-2">
                      {item.label}
                    </div>
                    <div className="text-lg font-medium text-neutral-300">
                      {item.value}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        </section>

        {/* CTA Section */}
        <section className="py-32 px-6 border-t border-neutral-800">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.6 }}
            className="max-w-4xl mx-auto text-center"
          >
            <h2 className="text-5xl md:text-7xl font-bold tracking-tight mb-8">
              Ready to <span className="text-neutral-500">build</span>?
            </h2>
            <p className="text-xl text-neutral-400 mb-12 max-w-2xl mx-auto">
              Start building your enterprise application today. No setup required.
            </p>
            <motion.div
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Link to="/auth/register" params={{}}>
                <Button
                  size="lg"
                  className="bg-neutral-50 text-neutral-950 hover:bg-neutral-100 border-0 px-8 py-6 text-lg font-medium h-auto"
                >
                  Get Started Free
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
            </motion.div>
          </motion.div>
        </section>
      </div>
    </div>
  )
}

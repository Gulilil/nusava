import { Navbar } from "@/components/navbar"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Mail, Save, ImageIcon } from "lucide-react"

export default function ProfilePage() {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar title="Profile" />
      <main className="flex-1 p-6 space-y-6">
        <div className="flex items-center gap-6 mb-8">
          <div className="relative">
            <Avatar className="h-24 w-24">
              <AvatarImage src="/placeholder.svg?height=96&width=96" alt="Profile" />
              <AvatarFallback>IB</AvatarFallback>
            </Avatar>
            <Button size="icon" className="absolute bottom-0 right-0 h-8 w-8 rounded-full">
              <ImageIcon className="h-4 w-4" />
            </Button>
          </div>
          <div>
            <h1 className="text-2xl font-bold">instabot_user</h1>
            <p className="text-muted-foreground">Manage your account settings and preferences</p>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Account Information</CardTitle>
            <CardDescription>Update your account details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <div className="flex">
                  <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-input bg-muted text-muted-foreground text-sm">
                    @
                  </span>
                  <Input id="username" defaultValue="instabot_user" className="rounded-l-none" />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <div className="flex">
                  <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-input bg-muted text-muted-foreground text-sm">
                    <Mail className="h-4 w-4" />
                  </span>
                  <Input id="email" type="email" defaultValue="user@example.com" className="rounded-l-none" />
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="bio">Bio</Label>
              <Textarea
                id="bio"
                placeholder="Tell us about yourself"
                defaultValue="Instagram automation enthusiast. Managing multiple accounts with ease."
                className="min-h-[100px]"
              />
            </div>
          </CardContent>
          <CardFooter>
            <Button className="ml-auto">
              <Save className="mr-2 h-4 w-4" />
              Save Changes
            </Button>
          </CardFooter>
        </Card>
      </main>
    </div>
  )
}

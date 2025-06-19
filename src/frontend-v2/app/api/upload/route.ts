import { NextResponse } from "next/server";
import path from "path";
import { writeFile, mkdir } from "fs/promises";

export const POST = async (req: Request) => {
  try {
    const formData = await req.formData();

    const file = formData.get("file") as File;
    if (!file) {
      return NextResponse.json({ error: "No files received." }, { status: 400 });
    }

    const buffer = Buffer.from(await file.arrayBuffer());
    const filename = Date.now() + "_" + file.name.replaceAll(" ", "_");
    const projectRoot = path.join(process.cwd(), '..', '..')
    const sharedUploadsDir = path.join(projectRoot, 'src/shared-uploads')
    
    // Ensure directory exists
    await mkdir(sharedUploadsDir, { recursive: true })
    // Save to shared directory
    const sharedPath = path.join(sharedUploadsDir, filename)
    await writeFile(sharedPath, buffer)

    // Also save to public for frontend preview
    const publicDir = path.join(process.cwd(), 'public', 'uploads')
    await mkdir(publicDir, { recursive: true })
    const publicPath = path.join(publicDir, filename)
    await writeFile(publicPath, buffer)

    return NextResponse.json({ 
      message: "Success", 
      filename: filename,
      localPath: sharedPath,
      url: `/uploads/${filename}`
    }, { status: 201 });
  } catch (error) {
    console.log("Error occurred ", error);
    return NextResponse.json({ message: "Failed", error: error }, { status: 500 });
  }
};
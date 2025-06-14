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
    
    // Ensure uploads directory exists
    const uploadsDir = path.join(process.cwd(), "public/uploads");
    try {
      await mkdir(uploadsDir, { recursive: true });
    } catch (error) {
      // Directory might already exist
    }

    const filepath = path.join(uploadsDir, filename);
    await writeFile(filepath, buffer);
    
    return NextResponse.json({ 
      message: "Success", 
      filename: filename,
      url: `/uploads/${filename}`
    }, { status: 201 });
  } catch (error) {
    console.log("Error occurred ", error);
    return NextResponse.json({ message: "Failed", error: error }, { status: 500 });
  }
};
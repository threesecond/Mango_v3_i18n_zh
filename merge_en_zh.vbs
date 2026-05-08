Option Explicit

Dim WshShell, strCurDir
Set WshShell = CreateObject("WScript.Shell")
Dim folder_select
folder_select=WshShell.CurrentDirectory
dim str_new_module
dim str_new_option

dim obj_fso,obj_folder,file_en,file_zh,file_output,content_en,content_zh,content_output
Set obj_fso = CreateObject("Scripting.FileSystemObject")
Dim obj_readStream, strData
Set obj_readStream = CreateObject("ADODB.Stream")
obj_readStream.CharSet = "utf-8"
obj_readStream.Open
'obj_readStream.LoadFromFile("C:\Users\admin\Desktop\ArtistCG\folder.txt")
'strData = objStream.ReadText()

For Each obj_folder In obj_fso.GetFolder(folder_select & "\modules\").SubFolders
    if str_new_option <> "" then str_new_option = str_new_option & vblf & vblf
    str_new_option = str_new_option & "==>" & obj_folder.Name
    if obj_fso.FileExists(obj_folder.Path & "\classes\i18n.properties" ) Then
        if obj_fso.FileExists(obj_folder.Path & "\classes\i18n_zh.properties" ) Then
            Set content_output = CreateObject("System.Collections.ArrayList")
            obj_readStream.LoadFromFile(obj_folder.Path & "\classes\i18n.properties")
            content_en = obj_readStream.ReadText()
            obj_readStream.LoadFromFile(obj_folder.Path & "\classes\i18n_zh.properties")
            content_zh = obj_readStream.ReadText()
            dim arr_en,arr_zh,tmpstr_en
            arr_en = Split(content_en,vblf)
            arr_zh = Split(content_zh,vblf)
            For Each tmpstr_en In arr_en
                if tmpstr_en <> "" then
                    dim arr_tmp
                    arr_tmp = Split(tmpstr_en,"=")
                    dim index
                    'msgbox arr_tmp(0)
                    index = fn_arr_indexof(arr_zh,arr_tmp(0))
                    if index <> -1 then
                        content_output.add arr_zh(index)
                    Else
                        if str_new_option <> "" then str_new_option = str_new_option & vblf
                        str_new_option = str_new_option & tmpstr_en
                        content_output.add tmpstr_en
                    End if
                
                Else
                    content_output.add ""
                End if
            Next

            Dim obj_writeStream
            Set obj_writeStream = CreateObject("ADODB.Stream")
            obj_writeStream.CharSet = "utf-8"
            obj_writeStream.Open
            
            dim tmparr
            For Each tmparr In content_output
                obj_writeStream.WriteText (tmparr) & vblf
            Next
            obj_writeStream.SaveToFile obj_folder.Path & "\classes\i18n_zh.properties", 2
            obj_writeStream.Close
            

            'WScript.Quit
        Else
            if str_new_module <> "" then str_new_module=str_new_module & ","
            str_new_module = str_new_module & obj_folder.Name
            obj_fso.CopyFile (obj_folder.Path & "\classes\i18n.properties") , (obj_folder.Path & "\classes\i18n_zh.properties")
        End if
    Else
        'WScript.Quit
    End if
Next

Set file_output = obj_fso.CreateTextFile(folder_select & "\merge_en_zh_log.log", 1)

file_output.Write ("Have All New Modules : " & vbcrlf & str_new_module) & vblf
file_output.Write ("Have Change : " & vbcrlf & str_new_option) & vblf
file_output.Close
msgbox "Done!"

Function fn_arr_indexof(ByRef arr, ByVal search)
    fn_arr_indexof = -1
    Dim i
    If IsArray(arr) Then
    
        For i = 0 To UBound(arr)
            if arr(i) <> "" then
                dim arr_tmp
                arr_tmp = Split(arr(i),"=")
                if arr_tmp(0) = search then
                    fn_arr_indexof = i
                    
                    Exit Function
                End if
            End if
        Next
    else
    end if
End Function


Function dialog_SelectFolder( myStartFolder )
    Dim sel_folder
    dim sel_shell
    On Error Resume Next
    SelectFolder = vbNull
    Set sel_shell  = CreateObject( "Shell.Application" )
    Set sel_folder = sel_shell.BrowseForFolder( 0, "Select Folder", 0, myStartFolder )
    If IsObject( sel_folder ) Then SelectFolder = sel_folder.Self.Path
    Set sel_folder = Nothing
    Set sel_shell  = Nothing
    On Error Goto 0
End Function